// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title StagQuest - A Simplified Novena Tracking NFT Contract
 * @notice This contract helps users grow in virtue and family life by tracking novenas via Stag NFTs.
 *         Users or the owner mint Stags with optional ETH commitments to signal dedication to breaking
 *         addictions (e.g., pornography) and supporting pro-life family causes. The owner completes
 *         novenas, upgrading familySize on 9/9 success, and logs successful days for AI analysis.
 *         Stags use standard ERC721 transfers for interoperability (e.g., claiming by new Web3 users).
 * @dev Deployed on Base Sepolia, uses ERC721Enumerable for NFT tracking and standard transfers.
 */
contract StagQuest is ERC721Enumerable, Ownable, ReentrancyGuard {
    // @notice Tracks the next available token ID for minting new Stags.
    uint256 public nextTokenId = 1;

    // @notice Minimum fee (0.0001 ETH) to mint a Stag; users can pay more to signal commitment.
    // @dev Funds owner gas costs (~0.001 ETH/novena completion); withdrawn to sustain operations.
    uint256 public minMintFee = 0.0001 ether;

    // @notice Maps each Stag (tokenId) to its family size, symbolizing growth in virtue and family commitment.
    // @dev Starts at 0, increments by 1 only on a perfect 9/9 novena, max 255 (uint8 limit).
    mapping(uint256 => uint8) public familySize;

    // @notice Tracks whether a Stag has an active novena in progress.
    // @dev True when started, False when inactive or completed; no daily updates—owner resolves all.
    mapping(uint256 => bool) public hasActiveNovena;

    // @notice Stores the number of successful days (0-9) from the last completed novena.
    // @dev Reset to 0 on start, updated on completion, logged in events for AI to trend progress over time.
    mapping(uint256 => uint8) public successfulDays;

    // @notice Emitted when a novena begins, signaling a user’s commitment to 9 days of growth.
    // @param stagId The Stag NFT starting the novena.
    // @param user The Stag’s owner, committed to virtue (e.g., purity, family restoration).
    // @param amount Optional ETH donated, reflecting dedication level for AI to note.
    event NovenaStarted(uint256 indexed stagId, address indexed user, uint256 amount);

    // @notice Emitted when a novena ends, logging success for AI encouragement and blockchain tracking.
    // @param stagId The Stag NFT completing the novena.
    // @param successfulDays Days succeeded (0-9), 9/9 required for familySize upgrade.
    event NovenaCompleted(uint256 indexed stagId, uint8 successfulDays);

    // @notice Emitted when a Stag’s familySize increases, celebrating a perfect 9/9 novena.
    // @param stagId The Stag NFT upgraded.
    // @param newSize The new familySize, symbolizing growth in virtue or family life.
    event FamilySizeUp(uint256 indexed stagId, uint8 newSize);

    /**
     * @notice Initializes the contract with the deployer as owner, managing all novena actions.
     */
    constructor() ERC721("StagQuest", "STQ") Ownable(msg.sender) {}

    /**
     * @notice Mints a new Stag NFT, starting a user’s journey toward virtue and family growth.
     * @dev Users pay a minimum fee (0.0001 ETH) or more to signal commitment; funds owner operations.
     *      Owner can mint for non-Web3 users, transferring later via standard ERC721 transferFrom.
     * @return stagId The newly minted Stag’s token ID.
     */
    function mintStag() external payable returns (uint256) {
        require(msg.value >= minMintFee, "Payment below minimum mint fee");
        uint256 stagId = nextTokenId++;
        _mint(msg.sender, stagId);
        familySize[stagId] = 0;
        successfulDays[stagId] = 0;
        return stagId;
    }

    /**
     * @notice Starts a novena for a Stag, with optional ETH to signal commitment.
     * @dev Callable by the Stag’s owner or contract owner (for non-Web3 users); ETH funds operations.
     * @param stagId The Stag NFT to begin the novena for.
     */
    function startNovena(uint256 stagId) external payable {
        require(ownerOf(stagId) == msg.sender || msg.sender == owner(), "Must be owner or contract owner");
        require(!hasActiveNovena[stagId], "This stag already has an active novena");
        hasActiveNovena[stagId] = true;
        successfulDays[stagId] = 0;  // Reset for new novena
        emit NovenaStarted(stagId, ownerOf(stagId), msg.value);
    }

    /**
     * @notice Completes a Stag’s novena, logging success and upgrading familySize if 9/9.
     * @dev Only the contract owner calls this, reporting total successful days (0-9) based on off-chain tracking.
     * @param stagId The Stag NFT to complete.
     * @param successfulDaysCount Number of days the user succeeded (0-9), 9 required for upgrade.
     */
    function completeNovena(uint256 stagId, uint8 successfulDaysCount) external onlyOwner {
        require(hasActiveNovena[stagId], "No active novena for this stag");
        require(successfulDaysCount <= 9, "Successful days cannot exceed 9");

        hasActiveNovena[stagId] = false;
        successfulDays[stagId] = successfulDaysCount;  // Log for trending

        if (successfulDaysCount == 9) {
            require(familySize[stagId] < 255, "Family size at maximum");
            familySize[stagId] += 1;
            emit FamilySizeUp(stagId, familySize[stagId]);
        }
        emit NovenaCompleted(stagId, successfulDaysCount);
    }

    /**
     * @notice Completes multiple Stags’ novenas in one transaction, optimizing gas costs.
     * @dev Owner uses this for efficiency (e.g., ~0.001 ETH for 5 completions vs. 0.0025 ETH individually).
     * @param stagIds Array of Stag NFTs to complete.
     * @param successes Array of successful days (0-9) per Stag, must match stagIds length.
     */
    function batchCompleteNovena(uint256[] calldata stagIds, uint8[] calldata successes) external onlyOwner {
        require(stagIds.length == successes.length, "Array lengths must match");

        for (uint256 i = 0; i < stagIds.length; i++) {
            uint256 stagId = stagIds[i];
            uint8 successfulDaysCount = successes[i];
            require(hasActiveNovena[stagId], "No active novena for this stag");
            require(successfulDaysCount <= 9, "Successful days cannot exceed 9");

            hasActiveNovena[stagId] = false;
            successfulDays[stagId] = successfulDaysCount;

            if (successfulDaysCount == 9) {
                require(familySize[stagId] < 255, "Family size at maximum");
                familySize[stagId] += 1;
                emit FamilySizeUp(stagId, familySize[stagId]);
            }
            emit NovenaCompleted(stagId, successfulDaysCount);
        }
    }

    /**
     * @notice Withdraws accumulated mint fees and novena donations to fund owner operations.
     * @dev Ensures owner can sustain gas costs (~0.0005 ETH/completion, ~0.001 ETH/batch).
     */
    function withdrawOwnerFunds() external onlyOwner nonReentrant {
        uint256 balance = address(this).balance;
        require(balance > 0, "No funds available to withdraw");
        payable(owner()).transfer(balance);
    }

    /**
     * @notice Adjusts the minimum mint fee to balance accessibility and funding.
     * @dev Owner can lower (e.g., 0 ETH) or raise based on gas needs.
     * @param newFee The new minimum mint fee in wei.
     */
    function setMintFee(uint256 newFee) external onlyOwner {
        minMintFee = newFee;
    }
}