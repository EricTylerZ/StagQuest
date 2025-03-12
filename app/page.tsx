'use client';

import React, { useState, useEffect } from 'react';
import { ConnectWallet } from '@coinbase/onchainkit/wallet';
import { useAccount, useReadContract, useWriteContract } from 'wagmi';
import { baseSepolia } from 'wagmi/chains';
import { ethers } from 'ethers';

// Replace with your actual contract address
const CONTRACT_ADDRESS = '0x5E1557B4C7Fc5268512E98662F23F923042FF5c5' as const;

// Full ABI for StagQuest contract
const CONTRACT_ABI = [
  {
    "inputs": [],
    "name": "mintStag",
    "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [{ "internalType": "uint256", "name": "stagId", "type": "uint256" }],
    "name": "startNovena",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      { "internalType": "uint256", "name": "stagId", "type": "uint256" },
      { "internalType": "uint8", "name": "successfulDays", "type": "uint8" }
    ],
    "name": "completeNovena",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      { "internalType": "uint256[]", "name": "stagIds", "type": "uint256[]" },
      { "internalType": "uint8[]", "name": "successes", "type": "uint8[]" }
    ],
    "name": "batchCompleteNovena",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "owner",
    "outputs": [{ "internalType": "address", "name": "", "type": "address" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [{ "internalType": "uint256", "name": "tokenId", "type": "uint256" }],
    "name": "ownerOf",
    "outputs": [{ "internalType": "address", "name": "", "type": "address" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [{ "internalType": "uint256", "name": "tokenId", "type": "uint256" }],
    "name": "familySize",
    "outputs": [{ "internalType": "uint8", "name": "", "type": "uint8" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [{ "internalType": "uint256", "name": "tokenId", "type": "uint256" }],
    "name": "hasActiveNovena",
    "outputs": [{ "internalType": "bool", "name": "", "type": "bool" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [{ "internalType": "uint256", "name": "tokenId", "type": "uint256" }],
    "name": "successfulDays",
    "outputs": [{ "internalType": "uint8", "name": "", "type": "uint8" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "nextTokenId",
    "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
    "stateMutability": "view",
    "type": "function"
  }
];

// Your provided Discord OAuth URL
const DISCORD_OAUTH_URL = 'https://discord.com/oauth2/authorize?client_id=1348188422367477842&redirect_uri=https%3A%2F%2Fstag-quest.vercel.app%2Fapi%2Fdiscord-callback&response_type=code&scope=identify';

// Stag interface
interface Stag {
  tokenId: number;
  owner: string;
  familySize: number;
  hasActiveNovena: boolean;
  successfulDays: number;
}

export default function Home() {
  const { address, isConnected, chainId } = useAccount();
  const [stags, setStags] = useState<Stag[]>([]);
  const [mintAmount, setMintAmount] = useState<string>('0.0001');
  const [novenaAmount, setNovenaAmount] = useState<string>('0.0001');
  const [successfulDays, setSuccessfulDays] = useState<{ [key: number]: string }>({});
  const [batchStagIds, setBatchStagIds] = useState<string>('');
  const [batchSuccesses, setBatchSuccesses] = useState<string>('');

  // Wagmi hooks for contract interactions
  const { writeContract: mintStag, isPending: mintPending } = useWriteContract();
  const { writeContract: startNovenaFn, isPending: novenaPending } = useWriteContract();
  const { writeContract: completeNovenaFn, isPending: completePending } = useWriteContract();
  const { writeContract: batchCompleteNovenaFn, isPending: batchPending } = useWriteContract();

  // Check if user is the contract owner
  const { data: owner } = useReadContract({
    address: CONTRACT_ADDRESS,
    abi: CONTRACT_ABI,
    functionName: 'owner',
    chainId: baseSepolia.id,
  }) as { data: string | undefined };

  const isOwner = address && owner && address.toLowerCase() === owner.toLowerCase();

  // Fetch stag statuses
  useEffect(() => {
    if (!isConnected || !address) return;

    const fetchStagStatuses = async () => {
      try {
        const provider = new ethers.BrowserProvider(window.ethereum);
        const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);
        const nextTokenId = await contract.nextTokenId();
        const stags: Stag[] = [];

        for (let i = 1; i < nextTokenId; i++) {
          try {
            const owner = await contract.ownerOf(i);
            if (isOwner || owner.toLowerCase() === address.toLowerCase()) {
              const familySize = await contract.familySize(i);
              const hasActiveNovena = await contract.hasActiveNovena(i);
              const successfulDays = await contract.successfulDays(i);
              stags.push({
                tokenId: i,
                owner,
                familySize: Number(familySize),
                hasActiveNovena,
                successfulDays: Number(successfulDays),
              });
            }
          } catch (error) {
            console.error(`Failed to fetch stag ${i}:`, error);
          }
        }
        setStags(stags);
      } catch (error) {
        console.error('Failed to fetch stags:', error);
      }
    };

    fetchStagStatuses();
  }, [address, isConnected, isOwner]);

  // Mint a stag
  const handleMintStag = () => {
    if (!isConnected || !address) {
      alert('Please connect your wallet.');
      return;
    }
    const amountInWei = ethers.parseEther(mintAmount);
    mintStag({
      address: CONTRACT_ADDRESS,
      abi: CONTRACT_ABI,
      functionName: 'mintStag',
      chainId: baseSepolia.id,
      value: amountInWei,
    }, {
      onSuccess: () => alert('Stag minted successfully!'),
      onError: (error) => alert(`Minting failed: ${error.message}`),
    });
  };

  // Start a novena
  const handleStartNovena = async (stagId: number) => {
    if (!isConnected || !address) {
      alert('Please connect your wallet.');
      return;
    }
    if (chainId !== baseSepolia.id) {
      alert('Please switch to Base Sepolia network.');
      return;
    }
    const amountInWei = ethers.parseEther(novenaAmount);
    startNovenaFn({
      address: CONTRACT_ADDRESS,
      abi: CONTRACT_ABI,
      functionName: 'startNovena',
      chainId: baseSepolia.id,
      args: [BigInt(stagId)],
      value: amountInWei,
    }, {
      onSuccess: async () => {
        alert('Novena started successfully!');
        // Notify backend for Discord prompts
        await fetch('/api/start-novena', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ stagId, ownerAddress: address }),
        });
      },
      onError: (error) => alert(`Failed to start novena: ${error.message}`),
    });
  };

  // Complete a novena (admin only)
  const handleCompleteNovena = (stagId: number) => {
    if (!isConnected || !isOwner) return;
    const days = parseInt(successfulDays[stagId] || '0');
    if (isNaN(days) || days > 9) {
      alert('Successful days must be 0-9.');
      return;
    }
    completeNovenaFn({
      address: CONTRACT_ADDRESS,
      abi: CONTRACT_ABI,
      functionName: 'completeNovena',
      chainId: baseSepolia.id,
      args: [BigInt(stagId), days],
    }, {
      onSuccess: () => alert('Novena completed successfully!'),
      onError: (error) => alert(`Failed to complete novena: ${error.message}`),
    });
  };

  // Batch complete novenas (admin only)
  const handleBatchCompleteNovena = () => {
    if (!isConnected || !isOwner) return;
    const stagIds = batchStagIds.split(',').map(id => BigInt(id.trim()));
    const successes = batchSuccesses.split(',').map(s => parseInt(s.trim()));
    if (stagIds.length === 0 || stagIds.length !== successes.length || successes.some(d => d > 9)) {
      alert('Invalid batch data: ensure all Stag IDs have valid days (0-9).');
      return;
    }
    batchCompleteNovenaFn({
      address: CONTRACT_ADDRESS,
      abi: CONTRACT_ABI,
      functionName: 'batchCompleteNovena',
      chainId: baseSepolia.id,
      args: [stagIds, successes],
    }, {
      onSuccess: () => {
        alert('Batch novena completion successful!');
        setBatchStagIds('');
        setBatchSuccesses('');
      },
      onError: (error) => alert(`Batch completion failed: ${error.message}`),
    });
  };

  // Discord login
  const handleDiscordLogin = () => {
    window.location.href = DISCORD_OAUTH_URL;
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>StagQuest {isOwner ? '(Admin)' : ''}</h1>
        <div>
          <ConnectWallet 
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 min-w-[150px] text-center"
            text={isConnected ? `Connected: ${address?.slice(0, 6)}...${address?.slice(-4)}` : 'Connect Wallet'}
          />
          <button
            onClick={handleDiscordLogin}
            style={{
              padding: '10px 20px',
              backgroundColor: '#7289da',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              marginLeft: '10px',
            }}
          >
            Login with Discord
          </button>
        </div>
      </header>

      {isConnected ? (
        <main>
          {/* Mint Section */}
          <div style={{ marginBottom: '20px' }}>
            <label>Mint Amount (ETH, min 0.0001):</label>
            <input
              type="number"
              step="0.0001"
              value={mintAmount}
              onChange={(e) => setMintAmount(e.target.value)}
              style={{ padding: '5px', marginRight: '10px' }}
            />
            <button
              onClick={handleMintStag}
              disabled={mintPending}
              style={{ padding: '10px 20px', backgroundColor: mintPending ? '#ccc' : '#0070f3', color: 'white' }}
            >
              {mintPending ? 'Minting...' : 'Mint Stag'}
            </button>
          </div>

          {/* Stag List */}
          <h2>{isOwner ? 'All Stags' : 'Your Stags'}</h2>
          {stags.length > 0 ? (
            stags.map((stag) => (
              <div key={stag.tokenId} style={{ border: '1px solid #ddd', padding: '10px', marginBottom: '10px' }}>
                <p>Stag ID: {stag.tokenId}</p>
                <p>Owner: {stag.owner}</p>
                <p>Family Size: {stag.familySize}</p>
                <p>Active Novena: {stag.hasActiveNovena ? 'Yes' : 'No'}</p>
                <p>Successful Days: {stag.successfulDays}</p>

                {!stag.hasActiveNovena && (
                  <>
                    <input
                      type="number"
                      step="0.0001"
                      value={novenaAmount}
                      onChange={(e) => setNovenaAmount(e.target.value)}
                      placeholder="Novena Amount (ETH)"
                      style={{ marginRight: '10px' }}
                    />
                    <button
                      onClick={() => handleStartNovena(stag.tokenId)}
                      disabled={novenaPending}
                      style={{ padding: '5px 10px', backgroundColor: novenaPending ? '#ccc' : '#4CAF50', color: 'white' }}
                    >
                      {novenaPending ? 'Starting...' : 'Start Novena'}
                    </button>
                  </>
                )}

                {isOwner && stag.hasActiveNovena && (
                  <>
                    <input
                      type="number"
                      min="0"
                      max="9"
                      value={successfulDays[stag.tokenId] || ''}
                      onChange={(e) => setSuccessfulDays({ ...successfulDays, [stag.tokenId]: e.target.value })}
                      placeholder="Successful Days (0-9)"
                      style={{ marginRight: '10px' }}
                    />
                    <button
                      onClick={() => handleCompleteNovena(stag.tokenId)}
                      disabled={completePending}
                      style={{ padding: '5px 10px', backgroundColor: completePending ? '#ccc' : '#F44336', color: 'white' }}
                    >
                      {completePending ? 'Completing...' : 'Complete Novena'}
                    </button>
                  </>
                )}
              </div>
            ))
          ) : (
            <p>No stags found. Mint one to start!</p>
          )}

          {/* Batch Complete (Admin Only) */}
          {isOwner && (
            <div style={{ marginTop: '20px' }}>
              <h2>Batch Complete Novenas</h2>
              <input
                type="text"
                value={batchStagIds}
                onChange={(e) => setBatchStagIds(e.target.value)}
                placeholder="Stag IDs (comma-separated)"
                style={{ marginRight: '10px' }}
              />
              <input
                type="text"
                value={batchSuccesses}
                onChange={(e) => setBatchSuccesses(e.target.value)}
                placeholder="Successful Days (comma-separated)"
                style={{ marginRight: '10px' }}
              />
              <button
                onClick={handleBatchCompleteNovena}
                disabled={batchPending}
                style={{ padding: '5px 10px', backgroundColor: batchPending ? '#ccc' : '#2196F3', color: 'white' }}
              >
                {batchPending ? 'Completing...' : 'Batch Complete'}
              </button>
            </div>
          )}
        </main>
      ) : (
        <p>Please connect your wallet to continue.</p>
      )}
    </div>
  );
}