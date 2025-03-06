// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

// StagQuest: A contract to help users overcome addiction, build virtue, and fight human trafficking
// Users mint Stag (Cervus) NFTs, stake ETH for a 9-day novena, and aim to stay porn-free
// Success grows the stag’s family (Cervus -> Cerva -> Cervulus); failures donate to anti-trafficking
// FamilySize: 0 = lone Cervus, 1 = Cervus + Cerva, 2 = Cervus + Cerva + Cervulus, 3 = Cervus + Cerva + 2 Cervuli, etc.
// An off-chain oracle (bot) reports daily success after 7 messages, users report to it, not the contract
contract StagQuest is ERC721Enumerable, Ownable, ReentrancyGuard {
    uint256 public nextTokenId = 1;           // Next ID for minting new NFTs
    uint256 public minMintFee = 0.0001 ether; // Minimum fee to mint a Cervus
    uint256 public minNovenaStake = 0.0009 ether; // Minimum stake for a novena
    address public regenAddress;              // Address for anti-trafficking donations
    address public oracle;                    // Oracle address for reporting success

    mapping(uint256 => uint8) public familySize;     // 0 = Cervus, 1 = +Cerva, 2 = +Cervulus, etc.
    mapping(uint256 => uint256) public activeStakes; // ETH staked for a novena
    mapping(uint256 => uint8) public daysCompleted;  // Days completed in current novena (0-9)
    mapping(uint256 => uint8) public successfulDays; // Successful days in current novena (0-9)
    mapping(uint256 => bool) public hasActiveNovena; // Active novena flag
    mapping(address => uint256) public pendingWithdrawals; // Withdrawable funds

    event NovenaStarted(uint256 indexed stagId, address indexed user, uint256 stake);
    event DayResolved(uint256 indexed stagId, bool success);
    event NovenaCompleted(uint256 indexed stagId, uint8 successfulDays);
    event FamilySizeUp(uint256 indexed stagId, uint8 newSize);

    constructor(address initialRegenAddress) ERC721("StagQuest", "STQ") Ownable(msg.sender) {
        require(initialRegenAddress != address(0), "Regen address cannot be zero");
        regenAddress = initialRegenAddress;
        oracle = msg.sender; // Initially owner; update to bot later
    }

    // Mint a new Stag (Cervus) NFT
    function mintStag() external payable returns (uint256) {
        require(msg.value >= minMintFee, "Payment below minimum mint fee");
        uint256 stagId = nextTokenId++;
        _mint(msg.sender, stagId);
        familySize[stagId] = 0;
        return stagId;
    }

    // Start a 9-day novena, user stakes ETH
    function startNovena(uint256 stagId) external payable {
        require(ownerOf(stagId) == msg.sender, "You don’t own this stag");
        require(!hasActiveNovena[stagId], "This stag already has an active novena");
        require(msg.value >= minNovenaStake, "Stake below minimum required");

        activeStakes[stagId] = msg.value;
        hasActiveNovena[stagId] = true;
        daysCompleted[stagId] = 0;
        successfulDays[stagId] = 0;
        emit NovenaStarted(stagId, msg.sender, msg.value);
    }

    // Oracle reports daily success (1 check-in per day, after 7 off-chain messages)
    function checkIn(uint256 stagId, bool success) external {
        require(msg.sender == oracle, "Only oracle can report success");
        require(hasActiveNovena[stagId], "No active novena for this stag");
        require(daysCompleted[stagId] < 9, "Novena already completed");

        daysCompleted[stagId] += 1;
        if (success) {
            successfulDays[stagId] += 1;
        }
        emit DayResolved(stagId, success);

        if (daysCompleted[stagId] == 9) {
            _resolveNovena(stagId);
        }
    }

    // Resolve novena: 9/10ths to user on full success (1/10th per day), 1/10th to oracle
    function _resolveNovena(uint256 stagId) internal {
        hasActiveNovena[stagId] = false;
        uint256 stake = activeStakes[stagId];
        activeStakes[stagId] = 0;
        uint8 successes = successfulDays[stagId];
        emit NovenaCompleted(stagId, successes);

        address stagOwner = ownerOf(stagId);
        uint256 oracleCut = stake / 10; // 1/10th of total stake to oracle
        if (successes == 9) {
            // Full success: 9/10ths to user, 1/10th to oracle
            require(familySize[stagId] < 255, "Family size at maximum (255)");
            pendingWithdrawals[stagOwner] += (stake * 9) / 10; // 90% back
            pendingWithdrawals[oracle] += oracleCut;           // 10% fee
            familySize[stagId] += 1;
            emit FamilySizeUp(stagId, familySize[stagId]);
        } else {
            // Partial success: 1/10th per success to user, 1/10th per fail to regen, 1/10th to oracle
            uint256 failedDays = 9 - successes;
            uint256 toRegen = (stake / 10) * failedDays;     // Failed portion to regen
            uint256 toUser = (stake / 10) * successes;       // Success portion to user
            pendingWithdrawals[regenAddress] += toRegen;
            pendingWithdrawals[stagOwner] += toUser;
            pendingWithdrawals[oracle] += oracleCut;         // Oracle gets 1/10th regardless
        }

        daysCompleted[stagId] = 0;
        successfulDays[stagId] = 0;
    }

    // Withdraw pending funds
    function withdrawPending() external nonReentrant {
        uint256 amount = pendingWithdrawals[msg.sender];
        require(amount > 0, "No funds available to withdraw");
        pendingWithdrawals[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
    }

    // Owner withdraws uncommitted funds (e.g., mint fees)
    function withdrawOwnerFunds() external onlyOwner nonReentrant {
        uint256 lockedStakes = 0;
        for (uint256 i = 1; i < nextTokenId; i++) {
            lockedStakes += activeStakes[i];
        }
        uint256 available = address(this).balance - lockedStakes;
        require(available > 0, "No funds available to withdraw");
        payable(owner()).transfer(available);
    }

    // Transfer a stag (only if no active novena)
    function transferStag(uint256 stagId, address to) external {
        require(ownerOf(stagId) == msg.sender, "You don’t own this stag");
        require(!hasActiveNovena[stagId], "Cannot transfer a stag with active novena");
        transferFrom(msg.sender, to, stagId);
    }

    // Owner adjusts minimum fees
    function setMinMintFee(uint256 newFee) external onlyOwner {
        require(newFee > 0, "Mint fee must be positive");
        minMintFee = newFee;
    }

    function setMinNovenaStake(uint256 newStake) external onlyOwner {
        require(newStake > 0, "Novena stake must be positive");
        minNovenaStake = newStake;
    }

    // Owner updates regen address
    function setRegenAddress(address newRegenAddress) external onlyOwner {
        require(newRegenAddress != address(0), "Regen address cannot be zero");
        regenAddress = newRegenAddress;
    }

    // Owner updates oracle address
    function setOracle(address newOracle) external onlyOwner {
        require(newOracle != address(0), "Oracle address cannot be zero");
        oracle = newOracle;
    }
}