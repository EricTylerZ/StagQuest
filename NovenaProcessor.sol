// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract NovenaProcessor is Ownable, ReentrancyGuard {
    address public stagQuest;
    uint256 public minDailyStake = 0.00009 ether;
    mapping(uint256 => uint256) public stakes;
    mapping(uint256 => uint256) public dailyStakes;
    mapping(uint256 => uint8) public daysCompleted;
    mapping(uint256 => uint8) public successfulDays;
    mapping(uint256 => bool) public hasActiveNovena;

    constructor(address _stagQuest) Ownable(msg.sender) {
        require(_stagQuest != address(0), "Invalid StagQuest address");
        stagQuest = _stagQuest;
    }

    function stake(uint256 stagId, uint256 totalAmount, uint256 dailyAmount) external payable {
        require(msg.value == totalAmount, "ETH must match total amount");
        require(dailyAmount >= minDailyStake, "Daily amount too low");
        require(totalAmount >= dailyAmount * 9, "Total must cover 9 days");
        require(StagQuest(stagQuest).ownerOf(stagId) == msg.sender, "Not your stag");
        require(!hasActiveNovena[stagId], "Novena already active");
        require(stakes[stagId] == 0, "Stag already staked");
        stakes[stagId] = totalAmount;
        dailyStakes[stagId] = dailyAmount;
        hasActiveNovena[stagId] = true;
    }

    function resolveDay(uint256 stagId, bool success) external onlyOwner nonReentrant {
        require(stakes[stagId] >= dailyStakes[stagId], "Insufficient stake");
        require(daysCompleted[stagId] < 9, "Novena complete");
        address stagOwner = StagQuest(stagQuest).ownerOf(stagId);
        uint256 dailyStake = dailyStakes[stagId];
        stakes[stagId] -= dailyStake;
        daysCompleted[stagId] += 1;
        if (success) successfulDays[stagId] += 1;
        if (daysCompleted[stagId] == 9) hasActiveNovena[stagId] = false;

        address regenAddress = StagQuest(stagQuest).regenAddress();
        bool isHerdMaster = StagQuest(stagQuest).isHerdMaster(stagOwner);
        address owner = StagQuest(stagQuest).owner();

        if (isHerdMaster && stagOwner != owner) {
            uint256 commission = (dailyStake * StagQuest(stagQuest).OWNER_COMMISSION()) / 100;
            uint256 herdMasterShare = dailyStake - commission;
            StagQuest(stagQuest).pendingWithdrawals(success ? stagOwner : regenAddress, herdMasterShare);
            StagQuest(stagQuest).pendingWithdrawals(owner, commission);
        } else {
            StagQuest(stagQuest).pendingWithdrawals(success ? stagOwner : regenAddress, dailyStake);
        }
    }

    function canMint(address user) external view returns (bool) {
        uint256 herdSize = StagQuest(stagQuest).balanceOf(user);
        if (herdSize == 0) return true;
        for (uint256 i = 0; i < herdSize; i++) {
            uint256 stagId = StagQuest(stagQuest).tokenOfOwnerByIndex(user, i);
            if (daysCompleted[stagId] < 9 && hasActiveNovena[stagId]) return false;
        }
        return true;
    }

    function isNovenaComplete(uint256 stagId) external view returns (bool) {
        return daysCompleted[stagId] == 9 || !hasActiveNovena[stagId];
    }

    function setMinDailyStake(uint256 newStake) external onlyOwner {
        require(newStake > 0, "Stake must be positive");
        minDailyStake = newStake;
    }

    function setStagQuest(address newStagQuest) external onlyOwner {
        require(newStagQuest != address(0), "Invalid StagQuest address");
        stagQuest = newStagQuest;
    }
}

interface StagQuest {
    function ownerOf(uint256 stagId) external view returns (address);
    function balanceOf(address owner) external view returns (uint256);
    function tokenOfOwnerByIndex(address owner, uint256 index) external view returns (uint256);
    function regenAddress() external view returns (address);
    function isHerdMaster(address user) external view returns (bool);
    function owner() external view returns (address);
    function OWNER_COMMISSION() external view returns (uint8);
    function pendingWithdrawals(address user, uint256 amount) external;
}