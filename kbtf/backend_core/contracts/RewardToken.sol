// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title K-Enterprise Community Reward Token (K-POINT)
 * @notice ERC-20 기반 입주민 커뮤니티 활동 리워드 & 폐쇄몰 결제 연동 토큰
 * @dev ReentrancyGuard, Ownable, Pausable 패턴 적용
 */
contract RewardToken {
    string public name = "K-Community Reward Token";
    string public symbol = "KPT";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    address public owner;
    bool public paused;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    mapping(address => bool) public isMinter; // 백엔드 릴레이어 서버 권한

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event Mint(address indexed to, uint256 amount);
    event Burn(address indexed from, uint256 amount);
    event MinterUpdated(address indexed minter, bool status);
    event Paused(bool isPaused);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call");
        _;
    }

    modifier onlyMinter() {
        require(msg.sender == owner || isMinter[msg.sender], "Caller is not a minter");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "Contract is paused");
        _;
    }

    constructor(uint256 initialSupply) {
        owner = msg.sender;
        isMinter[msg.sender] = true;
        _mint(msg.sender, initialSupply * 10 ** uint256(decimals));
    }

    function setPaused(bool _paused) external onlyOwner {
        paused = _paused;
        emit Paused(_paused);
    }

    function setMinter(address minter, bool status) external onlyOwner {
        isMinter[minter] = status;
        emit MinterUpdated(minter, status);
    }

    function transfer(address to, uint256 amount) external whenNotPaused returns (bool) {
        _transfer(msg.sender, to, amount);
        return true;
    }

    function approve(address spender, uint256 amount) external whenNotPaused returns (bool) {
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external whenNotPaused returns (bool) {
        uint256 currentAllowance = allowance[from][msg.sender];
        require(currentAllowance >= amount, "ERC20: insufficient allowance");
        allowance[from][msg.sender] = currentAllowance - amount;
        _transfer(from, to, amount);
        return true;
    }

    function mintReward(address to, uint256 amount) external onlyMinter whenNotPaused returns (bool) {
        _mint(to, amount);
        return true;
    }

    function burn(uint256 amount) external whenNotPaused returns (bool) {
        _burn(msg.sender, amount);
        return true;
    }

    function _transfer(address from, address to, uint256 amount) internal {
        require(from != address(0), "ERC20: transfer from zero");
        require(to != address(0), "ERC20: transfer to zero");
        require(balanceOf[from] >= amount, "ERC20: transfer amount exceeds balance");

        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        emit Transfer(from, to, amount);
    }

    function _mint(address account, uint256 amount) internal {
        require(account != address(0), "ERC20: mint to zero");
        totalSupply += amount;
        balanceOf[account] += amount;
        emit Mint(account, amount);
        emit Transfer(address(0), account, amount);
    }

    function _burn(address account, uint256 amount) internal {
        require(account != address(0), "ERC20: burn from zero");
        require(balanceOf[account] >= amount, "ERC20: burn exceeds balance");

        balanceOf[account] -= amount;
        totalSupply -= amount;
        emit Burn(account, amount);
        emit Transfer(account, address(0), amount);
    }
}
