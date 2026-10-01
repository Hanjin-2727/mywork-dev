// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title K-BTF Time Credit Smart Contract (시간크레딧)
 * @notice 자원봉사 및 돌봄 1시간 = 1 TimeCredit 적립 / 폐쇄몰 및 복지식권 소비 정산
 */
contract TimeCredit {
    string public name = "K-BTF Time Credit";
    string public symbol = "TC";
    uint8 public decimals = 2; // 1 TC = 100 subunits (0.01 시간 단위 정산)

    address public admin;
    mapping(bytes32 => uint256) public balances; // pseudo_uid => balance
    
    event CreditEarned(bytes32 indexed userUid, uint256 hoursAmount, string reason);
    event CreditSpent(bytes32 indexed userUid, uint256 hoursAmount, string item);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can execute");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function earnCredit(bytes32 userUid, uint256 amount, string calldata reason) external onlyAdmin {
        balances[userUid] += amount;
        emit CreditEarned(userUid, amount, reason);
    }

    function spendCredit(bytes32 userUid, uint256 amount, string calldata item) external onlyAdmin {
        require(balances[userUid] >= amount, "Insufficient Time Credit");
        balances[userUid] -= amount;
        emit CreditSpent(userUid, amount, item);
    }

    function getBalance(bytes32 userUid) external view returns (uint256) {
        return balances[userUid];
    }
}
