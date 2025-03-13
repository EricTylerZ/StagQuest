'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { useAccount, useReadContract, useWriteContract, useWaitForTransactionReceipt } from 'wagmi';
import { baseSepolia } from 'wagmi/chains';
import { ethers } from 'ethers';

// Dynamically import ConnectWallet to avoid SSR issues
const ConnectWallet = dynamic(() => import('@coinbase/onchainkit/wallet').then(mod => mod.ConnectWallet), { ssr: false });

const CONTRACT_ADDRESS = '0x5E1557B4C7Fc5268512E98662F23F923042FF5c5' as const;

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

const DISCORD_OAUTH_URL = 'https://discord.com/oauth2/authorize?client_id=1348188422367477842&redirect_uri=https%3A%2F%2Fstag-quest.vercel.app%2Fapi%2Fdiscord-callback&response_type=code&scope=identify';

// Interfaces
interface Stag {
  tokenId: number;
  owner: string;
  familySize: number;
  hasActiveNovena: boolean;
  successfulDays: number;
}

interface StagMetadata {
  discordId: string;
  email: string;
  utcOffset: string;
  preferredChannel: 'discord' | 'email' | 'text' | 'telegram';
}

interface UserProfile {
  walletAddress: string;
  discordId: string;
  email: string;
  phone?: string;
  telegram?: string;
  utcOffset: string;
  preferredChannel: 'discord' | 'email' | 'text' | 'telegram';
}

export default function Home() {
  const { address, isConnected, chainId } = useAccount();
  const [stags, setStags] = useState<Stag[]>([]);
  const [mintAmount, setMintAmount] = useState<string>('0.0001');
  const [novenaAmount, setNovenaAmount] = useState<string>('0.0001');
  const [successfulDays, setSuccessfulDays] = useState<{ [key: number]: string }>({});
  const [batchStagIds, setBatchStagIds] = useState<string>('');
  const [batchSuccesses, setBatchSuccesses] = useState<string>('');
  const [stagData, setStagData] = useState<{ [key: number]: StagMetadata }>({});
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

  const { writeContract: mintStag, data: mintTxHash, isPending: mintPending } = useWriteContract();
  const { writeContract: startNovenaFn, data: startTxHash, isPending: novenaPending } = useWriteContract();
  const { writeContract: completeNovenaFn, data: completeTxHash, isPending: completePending } = useWriteContract();
  const { writeContract: batchCompleteNovenaFn, data: batchTxHash, isPending: batchPending } = useWriteContract();

  const mintReceipt = useWaitForTransactionReceipt({ hash: mintTxHash });
  const startReceipt = useWaitForTransactionReceipt({ hash: startTxHash });
  const completeReceipt = useWaitForTransactionReceipt({ hash: completeTxHash });
  const batchReceipt = useWaitForTransactionReceipt({ hash: batchTxHash });

  const { data: owner } = useReadContract({
    address: CONTRACT_ADDRESS,
    abi: CONTRACT_ABI,
    functionName: 'owner',
    chainId: baseSepolia.id,
  }) as { data: string | undefined };

  const isOwner = address && owner && address.toLowerCase() === owner.toLowerCase();

  // Fetch user profile from Blob
  useEffect(() => {
    const fetchUserProfile = async () => {
      if (!isConnected || !address) return;
      try {
        const response = await fetch(`https://pmqhhpdds64stpmu.public.blob.vercel-storage.com/users/${address}.json`);
        if (response.ok) {
          const profile: UserProfile = await response.json();
          setUserProfile(profile);
        } else {
          const defaultProfile: UserProfile = {
            walletAddress: address,
            discordId: '',
            email: '',
            phone: '',
            telegram: '',
            utcOffset: '-7',
            preferredChannel: 'discord',
          };
          setUserProfile(defaultProfile);
          await fetch('/api/save-user-profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(defaultProfile),
          });
        }
      } catch (error) {
        console.error('Failed to fetch user profile:', error);
      }
    };
    fetchUserProfile();
  }, [address, isConnected]);

  // Fetch stag statuses from blockchain and Blob
  const fetchStagStatuses = async () => {
    if (!isConnected || !address) return;
    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);
      const nextTokenId = await contract.nextTokenId();
      const newStags: Stag[] = [];
      const newStagData: { [key: number]: StagMetadata } = { ...stagData };

      for (let i = 1; i < nextTokenId; i++) {
        try {
          const owner = await contract.ownerOf(i);
          if (isOwner || owner.toLowerCase() === address.toLowerCase()) {
            const familySize = await contract.familySize(i);
            const hasActiveNovena = await contract.hasActiveNovena(i);
            const successfulDays = await contract.successfulDays(i);
            newStags.push({
              tokenId: i,
              owner,
              familySize: Number(familySize),
              hasActiveNovena,
              successfulDays: Number(successfulDays),
            });

            // Fetch metadata from Blob if not already in stagData
            if (!newStagData[i]) {
              const blobResponse = await fetch(`https://pmqhhpdds64stpmu.public.blob.vercel-storage.com/stags/${i}.json`);
              if (blobResponse.ok) {
                const blobData = await blobResponse.json();
                newStagData[i] = {
                  discordId: blobData.discordId || '',
                  email: blobData.email || '',
                  utcOffset: blobData.utcOffset || '-7',
                  preferredChannel: blobData.preferredChannel || 'discord',
                };
              }
            }
          }
        } catch (error) {
          console.error(`Failed to fetch stag ${i}:`, error);
        }
      }
      setStags(newStags);
      setStagData(newStagData);
    } catch (error) {
      console.error('Failed to fetch stags:', error);
    }
  };

  useEffect(() => {
    fetchStagStatuses();
  }, [address, isConnected, isOwner]);

  // Save stag metadata to Blob via API
  const saveStagMetadata = async (stagId: number) => {
    if (!address) return;
    const metadata: StagMetadata = {
      discordId: stagData[stagId]?.discordId || '',
      email: stagData[stagId]?.email || '',
      utcOffset: stagData[stagId]?.utcOffset || '-7',
      preferredChannel: stagData[stagId]?.preferredChannel || 'discord',
    };
    try {
      const response = await fetch('/api/save-stag-metadata', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          stagId,
          ownerAddress: address,
          ...metadata,
        }),
      });
      if (response.ok) {
        alert(`Metadata for Stag ID ${stagId} saved successfully!`);
      } else {
        throw new Error('Failed to save metadata');
      }
    } catch (error) {
      console.error(`Failed to save metadata for stag ${stagId}:`, error);
      alert('Failed to save metadata.');
    }
  };

  // Mint a stag
  const handleMintStag = async () => {
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
    });
  };

  useEffect(() => {
    if (mintReceipt.data?.status === 'success') {
      alert('Stag minted successfully!');
      fetchStagStatuses();
    } else if (mintReceipt.data?.status === 'reverted') {
      alert('Minting failed on blockchain.');
    }
  }, [mintReceipt.data]);

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
    const discordId = stagData[stagId]?.discordId || '';
    const email = stagData[stagId]?.email || '';
    const utcOffset = stagData[stagId]?.utcOffset || '-7';
    const preferredChannel = stagData[stagId]?.preferredChannel || 'discord';
    if (!discordId && preferredChannel === 'discord') {
      alert('Please enter a Discord ID for this stag.');
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
    });
  };

  useEffect(() => {
    if (startReceipt.data?.status === 'success') {
      alert('Novena started successfully on blockchain!');
      fetchStagStatuses();
    } else if (startReceipt.data?.status === 'reverted') {
      alert('Novena start failed on blockchain.');
    }
  }, [startReceipt.data]);

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
    });
  };

  useEffect(() => {
    if (completeReceipt.data?.status === 'success') {
      alert('Novena completed successfully!');
      fetchStagStatuses();
    } else if (completeReceipt.data?.status === 'reverted') {
      alert('Novena completion failed on blockchain.');
    }
  }, [completeReceipt.data]);

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
    });
  };

  useEffect(() => {
    if (batchReceipt.data?.status === 'success') {
      alert('Batch novena completion successful!');
      setBatchStagIds('');
      setBatchSuccesses('');
      fetchStagStatuses();
    } else if (batchReceipt.data?.status === 'reverted') {
      alert('Batch completion failed on blockchain.');
    }
  }, [batchReceipt.data]);

  // Refresh stag statuses
  const handleRefreshStatus = () => {
    fetchStagStatuses();
    alert('Stag statuses refreshed!');
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

      {isConnected && (
        <main>
          {/* User Profile */}
          <div style={{ marginBottom: '20px' }}>
            <h2>Your Default Profile</h2>
            <label>Default Discord ID:</label>
            <input
              type="text"
              value={userProfile?.discordId || ''}
              onChange={(e) => setUserProfile(prev => prev ? { ...prev, discordId: e.target.value } : null)}
              placeholder="e.g., 123456789012345678"
              style={{ padding: '5px', marginRight: '10px', width: '200px' }}
            />
            <label>Default Email:</label>
            <input
              type="email"
              value={userProfile?.email || ''}
              onChange={(e) => setUserProfile(prev => prev ? { ...prev, email: e.target.value } : null)}
              placeholder="e.g., user@example.com"
              style={{ padding: '5px', marginRight: '10px', width: '200px' }}
            />
            <label>Default Phone (future):</label>
            <input
              type="text"
              value={userProfile?.phone || ''}
              onChange={(e) => setUserProfile(prev => prev ? { ...prev, phone: e.target.value } : null)}
              placeholder="e.g., +1234567890"
              style={{ padding: '5px', marginRight: '10px', width: '200px' }}
            />
            <label>Default Telegram (future):</label>
            <input
              type="text"
              value={userProfile?.telegram || ''}
              onChange={(e) => setUserProfile(prev => prev ? { ...prev, telegram: e.target.value } : null)}
              placeholder="e.g., @username"
              style={{ padding: '5px', marginRight: '10px', width: '200px' }}
            />
            <label>Default UTC Offset:</label>
            <input
              type="number"
              value={userProfile?.utcOffset || '-7'}
              onChange={(e) => setUserProfile(prev => prev ? { ...prev, utcOffset: e.target.value } : null)}
              style={{ padding: '5px', marginRight: '10px', width: '100px' }}
            />
            <label>Default Preferred Channel:</label>
            <select
              value={userProfile?.preferredChannel || 'discord'}
              onChange={(e) => setUserProfile(prev => prev ? { ...prev, preferredChannel: e.target.value as 'discord' | 'email' | 'text' | 'telegram' } : null)}
              style={{ padding: '5px' }}
            >
              <option value="discord">Discord</option>
              <option value="email">Email</option>
              <option value="text">Text (future)</option>
              <option value="telegram">Telegram (future)</option>
            </select>
          </div>

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

          {/* Refresh Status */}
          <div style={{ marginBottom: '20px' }}>
            <button
              onClick={handleRefreshStatus}
              style={{ padding: '10px 20px', backgroundColor: '#ff9800', color: 'white' }}
            >
              Refresh Status
            </button>
          </div>

          {/* Batch Complete (Admin Only) */}
          {isOwner && (
            <div style={{ marginBottom: '20px' }}>
              <h2>Batch Complete Novenas</h2>
              <input
                type="text"
                value={batchStagIds}
                onChange={(e) => setBatchStagIds(e.target.value)}
                placeholder="Stag IDs (comma-separated)"
                style={{ marginRight: '10px', padding: '5px' }}
              />
              <input
                type="text"
                value={batchSuccesses}
                onChange={(e) => setBatchSuccesses(e.target.value)}
                placeholder="Successful Days (comma-separated)"
                style={{ marginRight: '10px', padding: '5px' }}
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

                <div style={{ marginTop: '10px' }}>
                  <label>Discord ID:</label>
                  <input
                    type="text"
                    value={stagData[stag.tokenId]?.discordId || ''}
                    onChange={(e) => setStagData({
                      ...stagData,
                      [stag.tokenId]: { 
                        discordId: e.target.value, 
                        email: stagData[stag.tokenId]?.email || '', 
                        utcOffset: stagData[stag.tokenId]?.utcOffset || '-7',
                        preferredChannel: stagData[stag.tokenId]?.preferredChannel || 'discord'
                      }
                    })}
                    placeholder="e.g., 123456789012345678"
                    style={{ padding: '5px', marginRight: '10px', width: '200px' }}
                  />
                </div>
                <div style={{ marginTop: '10px' }}>
                  <label>Email:</label>
                  <input
                    type="email"
                    value={stagData[stag.tokenId]?.email || ''}
                    onChange={(e) => setStagData({
                      ...stagData,
                      [stag.tokenId]: { 
                        discordId: stagData[stag.tokenId]?.discordId || '', 
                        email: e.target.value, 
                        utcOffset: stagData[stag.tokenId]?.utcOffset || '-7',
                        preferredChannel: stagData[stag.tokenId]?.preferredChannel || 'discord'
                      }
                    })}
                    placeholder="e.g., user@example.com"
                    style={{ padding: '5px', marginRight: '10px', width: '200px' }}
                  />
                </div>
                <div style={{ marginTop: '10px' }}>
                  <label>UTC Offset:</label>
                  <input
                    type="number"
                    value={stagData[stag.tokenId]?.utcOffset || '-7'}
                    onChange={(e) => setStagData({
                      ...stagData,
                      [stag.tokenId]: { 
                        discordId: stagData[stag.tokenId]?.discordId || '', 
                        email: stagData[stag.tokenId]?.email || '', 
                        utcOffset: e.target.value,
                        preferredChannel: stagData[stag.tokenId]?.preferredChannel || 'discord'
                      }
                    })}
                    style={{ padding: '5px', marginRight: '10px', width: '100px' }}
                  />
                </div>
                <div style={{ marginTop: '10px' }}>
                  <label>Preferred Channel:</label>
                  <select
                    value={stagData[stag.tokenId]?.preferredChannel || 'discord'}
                    onChange={(e) => setStagData({
                      ...stagData,
                      [stag.tokenId]: { 
                        discordId: stagData[stag.tokenId]?.discordId || '', 
                        email: stagData[stag.tokenId]?.email || '', 
                        utcOffset: stagData[stag.tokenId]?.utcOffset || '-7',
                        preferredChannel: e.target.value as 'discord' | 'email' | 'text' | 'telegram'
                      }
                    })}
                    style={{ padding: '5px' }}
                  >
                    <option value="discord">Discord</option>
                    <option value="email">Email</option>
                    <option value="text">Text (future)</option>
                    <option value="telegram">Telegram (future)</option>
                  </select>
                </div>
                <div style={{ marginTop: '10px' }}>
                  <button
                    onClick={() => saveStagMetadata(stag.tokenId)}
                    style={{ padding: '5px 10px', backgroundColor: '#28a745', color: 'white' }}
                  >
                    Save Information
                  </button>
                </div>

                {!stag.hasActiveNovena && (
                  <div style={{ marginTop: '10px' }}>
                    <input
                      type="number"
                      step="0.0001"
                      value={novenaAmount}
                      onChange={(e) => setNovenaAmount(e.target.value)}
                      placeholder="Novena Amount (ETH)"
                      style={{ marginRight: '10px', padding: '5px' }}
                    />
                    <button
                      onClick={() => handleStartNovena(stag.tokenId)}
                      disabled={novenaPending}
                      style={{ padding: '5px 10px', backgroundColor: novenaPending ? '#ccc' : '#4CAF50', color: 'white' }}
                    >
                      {novenaPending ? 'Starting...' : 'Start Novena'}
                    </button>
                  </div>
                )}

                {isOwner && stag.hasActiveNovena && (
                  <div style={{ marginTop: '10px' }}>
                    <input
                      type="number"
                      min="0"
                      max="9"
                      value={successfulDays[stag.tokenId] || ''}
                      onChange={(e) => setSuccessfulDays(prev => ({ ...prev, [stag.tokenId]: e.target.value }))}
                      placeholder="Successful Days (0-9)"
                      style={{ marginRight: '10px', padding: '5px' }}
                    />
                    <button
                      onClick={() => handleCompleteNovena(stag.tokenId)}
                      disabled={completePending}
                      style={{ padding: '5px 10px', backgroundColor: completePending ? '#ccc' : '#F44336', color: 'white' }}
                    >
                      {completePending ? 'Completing...' : 'Complete Novena'}
                    </button>
                  </div>
                )}
              </div>
            ))
          ) : (
            <p>No stags found. Mint one to start!</p>
          )}
        </main>
      )}
    </div>
  );
}