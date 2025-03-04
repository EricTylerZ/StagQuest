// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract StagQuest is ERC721Enumerable, Ownable, ReentrancyGuard {
    uint256 public nextTokenId = 1;
    mapping(uint256 => uint256) public stakes;
    mapping(uint256 => uint256) public dailyStakes;
    mapping(uint256 => uint8) public daysCompleted;
    mapping(uint256 => uint8) public successfulDays;
    mapping(uint256 => bool) public hasActiveNovena;
    mapping(address => bool) public isHerdMaster;
    mapping(address => uint256) public pendingWithdrawals;
    uint256 public minMintFee = 0.00009 ether;
    uint256 public minDailyStake = 0.00009 ether;
    address public regenAddress;
    uint8 public constant OWNER_COMMISSION = 9; // 9%

    event HerdMasterStatusChanged(address indexed user, bool status);

    constructor(address initialRegenAddress) ERC721("StagQuest", "STQ") Ownable(msg.sender) {
        require(initialRegenAddress != address(0), "Invalid regen address");
        regenAddress = initialRegenAddress;
        isHerdMaster[msg.sender] = true;
    }

    function mint() external payable returns (uint256) {
        require(msg.value >= minMintFee, "Below minimum mint fee");
        if (!isHerdMaster[msg.sender]) {
            uint256 herdSize = balanceOf(msg.sender);
            require(
                herdSize == 0 || (herdSize > 0 && daysCompleted[tokenOfOwnerByIndex(msg.sender, 0)] == 9),
                "Finish your current stag's novena"
            );
        }
        uint256 stagId = nextTokenId++;
        _mint(msg.sender, stagId);
        hasActiveNovena[stagId] = true;
        return stagId;
    }

    function stake(uint256 stagId, uint256 totalAmount, uint256 dailyAmount) external payable {
        require(msg.value == totalAmount, "ETH must match total amount");
        require(dailyAmount >= minDailyStake, "Daily amount too low");
        require(totalAmount >= dailyAmount * 9, "Total must cover 9 days");
        require(ownerOf(stagId) == msg.sender, "Not your stag");
        require(hasActiveNovena[stagId], "Stag not active");
        require(stakes[stagId] == 0, "Stag already staked");
        stakes[stagId] = totalAmount;
        dailyStakes[stagId] = dailyAmount;
    }

    function resolveDay(uint256 stagId, bool success) external onlyOwner nonReentrant {
        require(stakes[stagId] >= dailyStakes[stagId], "Insufficient stake");
        require(daysCompleted[stagId] < 9, "Novena complete");
        stakes[stagId] -= dailyStakes[stagId];
        daysCompleted[stagId] += 1;
        if (success) successfulDays[stagId] += 1;
        if (daysCompleted[stagId] == 9) hasActiveNovena[stagId] = false;

        address stagOwner = ownerOf(stagId);
        uint256 dailyStake = dailyStakes[stagId];
        if (isHerdMaster[stagOwner] && stagOwner != owner()) {
            uint256 commission = (dailyStake * OWNER_COMMISSION) / 100;
            uint256 herdMasterShare = dailyStake - commission;
            pendingWithdrawals[success ? stagOwner : regenAddress] += herdMasterShare;
            pendingWithdrawals[owner()] += commission;
        } else {
            pendingWithdrawals[success ? stagOwner : regenAddress] += dailyStake;
        }
    }

    function transferStag(uint256 stagId, address to) external {
        require(ownerOf(stagId) == msg.sender, "Not your stag");
        require(!hasActiveNovena[stagId], "Cannot transfer active stag");
        _transfer(msg.sender, to, stagId);
    }

    function withdrawPending() external nonReentrant {
        uint256 amount = pendingWithdrawals[msg.sender];
        require(amount > 0, "No funds to withdraw");
        pendingWithdrawals[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
    }

    function withdraw() external onlyOwner nonReentrant {
        uint256 balance = address(this).balance;
        require(balance > 0, "No funds to withdraw");
        payable(owner()).transfer(balance);
    }

    function becomeHerdMasterByPayment() external payable {
        uint256 requiredPayment = minMintFee * 81;
        require(msg.value == requiredPayment, "Must send exactly 81x minMintFee");
        isHerdMaster[msg.sender] = true;
        emit HerdMasterStatusChanged(msg.sender, true);
    }

    function setHerdMaster(address herdMaster, bool status) external onlyOwner {
        isHerdMaster[herdMaster] = status;
        emit HerdMasterStatusChanged(herdMaster, status);
    }

    function setMinMintFee(uint256 newFee) external onlyOwner {
        require(newFee > 0, "Fee must be positive");
        minMintFee = newFee;
    }

    function setMinDailyStake(uint256 newStake) external onlyOwner {
        require(newStake > 0, "Stake must be positive");
        minDailyStake = newStake;
    }

    function setRegenAddress(address newRegenAddress) external onlyOwner {
        require(newRegenAddress != address(0), "Invalid address");
        regenAddress = newRegenAddress;
    }
}