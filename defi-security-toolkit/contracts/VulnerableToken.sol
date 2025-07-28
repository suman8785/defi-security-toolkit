// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableToken {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;
    address public owner;
    
    // Vulnerability: No access control
    constructor() {
        owner = msg.sender;
        totalSupply = 1000000 * 10**18;
        balances[owner] = totalSupply;
    }
    
    // Vulnerability: Reentrancy
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Vulnerability: External call before state update
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] -= amount;
    }
    
    // Vulnerability: Integer overflow (in older versions)
    function transfer(address to, uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        balances[msg.sender] -= amount;
        balances[to] += amount; // Potential overflow
    }
    
    // Vulnerability: tx.origin usage
    function ownerOnly() public view {
        require(tx.origin == owner, "Not owner");
    }
    
    // Vulnerability: Weak randomness
    function random() public view returns (uint256) {
        return uint256(keccak256(abi.encodePacked(block.timestamp, block.difficulty)));
    }
}