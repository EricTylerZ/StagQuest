// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract StagQuest is ERC721 {
    uint256 public tokenId;
    mapping(address => uint256) public stakes;

    constructor() ERC721("StagQuest", "STQ") {}

    function mint() external payable {
        require(msg.value >= 0.001 ether, "Min 0.001 ETH");
        tokenId++;
        _mint(msg.sender, tokenId);
    }

    function stake() external payable {
        require(msg.value >= 0.009 ether, "Min 0.009 ETH"); // 0.01/day for 9 days
        stakes[msg.sender] += msg.value;
    }

    function resolveDay(bool success, address regenAddr) external {
        uint256 amount = stakes[msg.sender];
        require(amount >= 0.001 ether, "Stake too low");
        stakes[msg.sender] -= 0.001 ether;
        if (success) {
            payable(msg.sender).transfer(0.001 ether);
        } else {
            payable(regenAddr).transfer(0.001 ether);
        }
    }
}