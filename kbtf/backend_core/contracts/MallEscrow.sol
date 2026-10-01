// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function transfer(address to, uint256 amount) external returns (bool);
}

/**
 * @title K-Enterprise Closed Mall Escrow Smart Contract
 * @notice 폐쇄형 거래몰 안전 결제 에스크로 컨트랙트
 * @dev 입금(예치 락) -> 구매확정 시 판매자 정산 / 주문취소 시 구매자 환불
 */
contract MallEscrow {
    address public admin;
    IERC20 public rewardToken;
    uint256 public platformFeePercent = 1; // 1% 플랫폼 수수료 (조정 가능)
    address public feeRecipient;

    enum EscrowStatus { PENDING, DEPOSITED, RELEASED, REFUNDED, DISPUTED }

    struct EscrowItem {
        bytes32 orderId;
        address buyer;
        address seller;
        uint256 tokenAmount;
        EscrowStatus status;
        uint256 createdAt;
        uint256 completedAt;
    }

    mapping(bytes32 => EscrowItem) public escrows;
    bool private _locked;

    event EscrowCreated(bytes32 indexed orderId, address indexed buyer, address indexed seller, uint256 tokenAmount);
    event EscrowReleased(bytes32 indexed orderId, address indexed seller, uint256 sellerAmount, uint256 feeAmount);
    event EscrowRefunded(bytes32 indexed orderId, address indexed buyer, uint256 refundAmount);
    event EscrowDisputed(bytes32 indexed orderId);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin allowed");
        _;
    }

    modifier nonReentrant() {
        require(!_locked, "ReentrancyGuard: locked");
        _locked = true;
        _;
        _locked = false;
    }

    constructor(address _rewardTokenAddress, address _feeRecipient) {
        admin = msg.sender;
        rewardToken = IERC20(_rewardTokenAddress);
        feeRecipient = _feeRecipient;
    }

    /**
     * @notice 구매자가 폐쇄몰 주문 결제 시 토큰 예치 (Escrow Lock)
     */
    function depositEscrow(bytes32 orderId, address seller, uint256 amount) external nonReentrant {
        require(escrows[orderId].tokenAmount == 0, "Escrow already exists for order");
        require(seller != address(0) && seller != msg.sender, "Invalid seller address");
        require(amount > 0, "Amount must be greater than 0");

        // 구매자 지갑에서 에스크로 컨트랙트로 토큰 이동 (사전 approve 필요)
        require(rewardToken.transferFrom(msg.sender, address(this), amount), "Token transfer failed");

        escrows[orderId] = EscrowItem({
            orderId: orderId,
            buyer: msg.sender,
            seller: seller,
            tokenAmount: amount,
            status: EscrowStatus.DEPOSITED,
            createdAt: block.timestamp,
            completedAt: 0
        });

        emit EscrowCreated(orderId, msg.sender, seller, amount);
    }

    /**
     * @notice 구매자가 물품 수령 확인 후 정산 승인 (판매자에게 정산 및 수수료 공제)
     */
    function releaseEscrow(bytes32 orderId) external nonReentrant {
        EscrowItem storage item = escrows[orderId];
        require(item.status == EscrowStatus.DEPOSITED, "Escrow is not in deposited state");
        require(msg.sender == item.buyer || msg.sender == admin, "Only buyer or admin can release");

        item.status = EscrowStatus.RELEASED;
        item.completedAt = block.timestamp;

        uint256 fee = (item.tokenAmount * platformFeePercent) / 100;
        uint256 sellerAmount = item.tokenAmount - fee;

        if (fee > 0) {
            require(rewardToken.transfer(feeRecipient, fee), "Fee transfer failed");
        }
        require(rewardToken.transfer(item.seller, sellerAmount), "Seller transfer failed");

        emit EscrowReleased(orderId, item.seller, sellerAmount, fee);
    }

    /**
     * @notice 주문 취소 또는 반품 시 구매자에게 100% 환불
     */
    function refundEscrow(bytes32 orderId) external nonReentrant {
        EscrowItem storage item = escrows[orderId];
        require(item.status == EscrowStatus.DEPOSITED || item.status == EscrowStatus.DISPUTED, "Cannot refund");
        require(msg.sender == item.seller || msg.sender == admin, "Only seller or admin can refund");

        item.status = EscrowStatus.REFUNDED;
        item.completedAt = block.timestamp;

        require(rewardToken.transfer(item.buyer, item.tokenAmount), "Refund transfer failed");

        emit EscrowRefunded(orderId, item.buyer, item.tokenAmount);
    }

    /**
     * @notice 에스크로 분쟁 발생 신고
     */
    function disputeEscrow(bytes32 orderId) external {
        EscrowItem storage item = escrows[orderId];
        require(item.status == EscrowStatus.DEPOSITED, "Invalid status for dispute");
        require(msg.sender == item.buyer || msg.sender == item.seller, "Only trade participants can dispute");

        item.status = EscrowStatus.DISPUTED;
        emit EscrowDisputed(orderId);
    }
}
