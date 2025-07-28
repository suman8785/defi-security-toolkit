pragma solidity ^0.8.0;

interface IFlashLoanProvider {
    function flashLoan(uint256 amount) external;
}

contract FlashLoanReceiver {
    address public owner;
    mapping(address => uint256) public profits;
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    // Vulnerability: No access control on flash loan execution
    function executeFlashLoan(
        address provider,
        uint256 amount,
        address target,
        bytes calldata data
    ) external {
        // Request flash loan
        IFlashLoanProvider(provider).flashLoan(amount);
        
        // Vulnerability: Arbitrary call
        (bool success, ) = target.call(data);
        require(success, "Flash loan execution failed");
        
        // Store profits (simplified)
        profits[msg.sender] += amount / 100; // 1% profit assumption
    }
    
    // Callback from flash loan provider
    function onFlashLoan(uint256 amount, uint256 fee) external {
        // Repay flash loan
        // In real implementation, would need actual repayment logic
    }
    
    // Vulnerability: No reentrancy protection
    function withdrawProfits() external {
        uint256 profit = profits[msg.sender];
        require(profit > 0, "No profits");
        
        (bool success, ) = msg.sender.call{value: profit}("");
        require(success, "Transfer failed");
        
        profits[msg.sender] = 0;
    }
}