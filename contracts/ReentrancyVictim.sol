// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ReentrancyVictim {
    mapping(address => uint256) public balances;
    
    event Deposit(address indexed user, uint256 amount);
    event Withdrawal(address indexed user, uint256 amount);
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }
    
    // Classic reentrancy vulnerability
    function withdraw() public {
        uint256 balance = balances[msg.sender];
        require(balance > 0, "No balance");
        
        // Vulnerability: External call before state update
        (bool success, ) = msg.sender.call{value: balance}("");
        require(success, "Transfer failed");
        
        // State update after external call
        balances[msg.sender] = 0;
        emit Withdrawal(msg.sender, balance);
    }
    
    // Another vulnerable function
    function withdrawAmount(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Vulnerability: External call before state update
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        // State update after external call
        balances[msg.sender] -= amount;
    }
    
    receive() external payable {
        deposit();
    }
}