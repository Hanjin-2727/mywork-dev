"""
[Core VC & VP Engine] W3C Verifiable Credential 2.0 및 Verifiable Presentation 모듈
익명 순수 자격화(Claim Anonymization) 및 선택적 공개(Selective Disclosure) 지원
"""
import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from .did_kms import CustodialKMS
from .security import ZeroPIISanitizer

class VCEngine:
    def __init__(self, kms: CustodialKMS, issuer_did: str = "did:kbtf:org:welfare_center_01"):
        self.kms = kms
        self.issuer_did = issuer_did
        self.issuer_key_id = "issuer-master-key"
        self.kms.generate_keypair(self.issuer_key_id)

    def issue_credential(
        self,
        holder_did: str,
        nfc_uid: str,
        credential_type: str,
        service_domain: str,
        validity_days: int = 14,
        subsidy_tier: str = "TIER_A"
    ) -> Dict[str, Any]:
        """순수 자격화(Zero-PII) 익명 VC 발급"""
        now = datetime.now(timezone.utc)
        exp = now + timedelta(days=validity_days)
        
        vc_id = f"urn:uuid:{uuid.uuid4()}"
        
        credential_subject = {
            "id": holder_did,
            "nfc_uid": nfc_uid,
            "service_domain": service_domain,
            "is_eligible": True,
            "subsidy_tier": subsidy_tier
        }
        
        # Zero-PII 검증
        ZeroPIISanitizer.audit_payload(credential_subject)

        payload_to_sign = json.dumps({
            "id": vc_id,
            "type": ["VerifiableCredential", credential_type],
            "issuer": self.issuer_did,
            "issuanceDate": now.isoformat(),
            "expirationDate": exp.isoformat(),
            "credentialSubject": credential_subject
        }, sort_keys=True)

        signature = self.kms.sign(self.issuer_key_id, payload_to_sign)

        vc = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://k-btf.or.kr/contexts/welfare-v1.jsonld"
            ],
            "id": vc_id,
            "type": ["VerifiableCredential", credential_type],
            "issuer": self.issuer_did,
            "issuanceDate": now.isoformat(),
            "expirationDate": exp.isoformat(),
            "credentialSubject": credential_subject,
            "proof": {
                "type": "Ed25519Signature2020",
                "created": now.isoformat(),
                "verificationMethod": f"{self.issuer_did}#{self.issuer_key_id}",
                "proofPurpose": "assertionMethod",
                "proofValue": signature
            }
        }
        return vc

    def verify_credential(self, vc: Dict[str, Any]) -> bool:
        """VC 발급자 서명 및 만료일자 무결성 검증"""
        proof = vc.get("proof", {})
        sig = proof.get("proofValue")
        if not sig:
            return False

        # 만료 확인
        exp_str = vc.get("expirationDate")
        if exp_str:
            exp_date = datetime.fromisoformat(exp_str)
            if datetime.now(timezone.utc) > exp_date:
                return False

        payload_to_verify = json.dumps({
            "id": vc["id"],
            "type": vc["type"],
            "issuer": vc["issuer"],
            "issuanceDate": vc["issuanceDate"],
            "expirationDate": vc["expirationDate"],
            "credentialSubject": vc["credentialSubject"]
        }, sort_keys=True)

        return self.kms.verify(self.issuer_key_id, payload_to_verify, sig)

    def create_verifiable_presentation(
        self,
        holder_did: str,
        holder_key_id: str,
        selected_vcs: List[Dict[str, Any]],
        nonce: Optional[str] = None
    ) -> Dict[str, Any]:
        """선택된 VC들로 구성된 동적 Verifiable Presentation (VP) 생성 및 홀더 서명"""
        now = datetime.now(timezone.utc)
        vp_id = f"urn:uuid:{uuid.uuid4()}"
        nonce_val = nonce or uuid.uuid4().hex

        payload_to_sign = json.dumps({
            "id": vp_id,
            "type": ["VerifiablePresentation"],
            "verifiableCredential": selected_vcs,
            "nonce": nonce_val
        }, sort_keys=True)

        holder_sig = self.kms.sign(holder_key_id, payload_to_sign)

        vp = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1"
            ],
            "id": vp_id,
            "type": ["VerifiablePresentation"],
            "verifiableCredential": selected_vcs,
            "proof": {
                "type": "Ed25519Signature2020",
                "created": now.isoformat(),
                "verificationMethod": f"{holder_did}#{holder_key_id}",
                "proofPurpose": "authentication",
                "nonce": nonce_val,
                "proofValue": holder_sig
            }
        }
        return vp

    def verify_presentation(self, vp: Dict[str, Any], holder_key_id: str) -> bool:
        """VP 서명 및 포함된 모든 VC 검증"""
        proof = vp.get("proof", {})
        sig = proof.get("proofValue")
        if not sig:
            return False

        payload_to_verify = json.dumps({
            "id": vp["id"],
            "type": vp["type"],
            "verifiableCredential": vp["verifiableCredential"],
            "nonce": proof.get("nonce")
        }, sort_keys=True)

        if not self.kms.verify(holder_key_id, payload_to_verify, sig):
            return False

        # 포함된 각 VC 검증
        for vc in vp.get("verifiableCredential", []):
            if not self.verify_credential(vc):
                return False

        return True
