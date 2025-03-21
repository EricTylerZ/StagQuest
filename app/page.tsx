'use client';

import React, { useState, useEffect } from 'react';
import { ConnectWallet } from '@coinbase/onchainkit/wallet';
import { useAccount, useReadContract, useWriteContract, useSwitchChain } from 'wagmi';
import { baseSepolia } from 'wagmi/chains';
import { Address } from 'viem';
import contractABI from '../data/abi.json';

const CONTRACT_ADDRESS = '0x5E1557B4C7Fc5268512E98662F23F923042FF5c5';
const MINIMUM_MINT_AMOUNT = BigInt('100000000000000');
const DISCORD_OAUTH_URL = 'https://discord.com/oauth2/authorize?client_id=1348188422367477842&redirect_uri=https%3A%2F%2Fstag-quest.vercel.app%2Fapi%2Fdiscord-callback&response_type=code&scope=identify';

export default function Home(): React.ReactNode {
  const { address, isConnected } = useAccount();
  const { switchChain } = useSwitchChain();
  const [mintResult, setMintResult] = useState<string | null>(null);
  const [stags, setStags] = useState<any[]>([]);
  const [isMounted, setIsMounted] = useState(false);
  const [mintAmount, setMintAmount] = useState<string>('0.0001');
  const [batchDays, setBatchDays] = useState<Record<number, string>>({});
  const [stagData, setStagData] = useState<Record<number, { timezone: string, discordId: string, email: string, novenaAmount: string }>>({});

  const API_URL = 'https://stag-quest.vercel.app';

  const { data: owner } = useReadContract({
    address: CONTRACT_ADDRESS,
    abi: contractABI,
    functionName: 'owner',
    chainId: baseSepolia.id,
  }) as { data: Address | undefined };

  const isOwner = address && owner && address.toLowerCase() === owner.toLowerCase();

  const { writeContract: mintStag, isPending: mintPending, error: mintError } = useWriteContract();
  const { writeContract: startNovenaFn, isPending: novenaPending, error: novenaError } = useWriteContract();
  const { writeContract: completeNovenaFn, isPending: completePending, error: completeError } = useWriteContract();
  const { writeContract: batchCompleteNovenaFn, isPending: batchPending, error: batchError } = useWriteContract();

  useEffect(() => {
    setIsMounted(true);
    if (address) {
      fetchStagStatus(address); // Initial fetch only on address change
      switchChain({ chainId: baseSepolia.id });
    }
  }, [address, switchChain]); // Removed stags from deps

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const discordId = urlParams.get('discordId');
    if (discordId && stags.length > 0) {
      setStagData(prev => ({ ...prev, [stags[0].tokenId]: { ...prev[stags[0].tokenId], discordId, timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC', email: '', novenaAmount: '0' } }));
    }
  }, [stags]); // Separate effect for OAuth redirect

  async function fetchStagStatus(address: string) {
    try {
      console.log('Fetching status for address:', address);
      const response = await fetch(`${API_URL}/api/status`, { mode: 'cors', cache: 'no-cache' });
      console.log('Response status:', response.status);
      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Server error: ${response.status} - ${text}`);
      }
      const data = await response.json();
      console.log('Status data:', data);
      if (data.stags) {
        const userStags = data.stags.filter((stag: any) => stag.owner.toLowerCase() === address.toLowerCase());
        setStags(isOwner ? data.stags : userStags);
        setMintResult(userStags.length > 0 ? null : "No stags found for this wallet.");
      } else {
        setMintResult("No stags found in response.");
      }
    } catch (error: any) {
      console.error('Fetch error:', error);
      setMintResult(`Failed to fetch status: ${error.message}`);
    }
  }

  const handleMint = () => {
    if (!isConnected || !address) {
      setMintResult("Please connect your wallet first.");
      return;
    }
    const amountInWei = BigInt(Math.floor(parseFloat(mintAmount) * 10**18));
    if (amountInWei < MINIMUM_MINT_AMOUNT) {
      setMintResult(`Amount must be at least 0.0001 ETH`);
      return;
    }
    mintStag({
      address: CONTRACT_ADDRESS,
      abi: contractABI,
      functionName: 'mintStag',
      chainId: baseSepolia.id,
      value: amountInWei,
    }, {
      onSuccess: () => {
        setMintResult("Stag minted successfully!");
        if (address) fetchStagStatus(address);
      },
      onError: (error) => setMintResult(`Minting failed: ${error.message}`),
    });
  };

  const handleStartNovena = async (tokenId: number) => {
    if (!isConnected || !address) {
      setMintResult("Please connect your wallet first.");
      return;
    }
    const { timezone, discordId, novenaAmount } = stagData[tokenId] || {};
    if (!timezone || !discordId) {
      setMintResult("Please set timezone and Discord ID for this Stag.");
      return;
    }
    const { data: stagOwner } = useReadContract({
      address: CONTRACT_ADDRESS,
      abi: contractABI,
      functionName: 'ownerOf',
      args: [BigInt(tokenId)],
      chainId: baseSepolia.id,
    }) as { data: Address | undefined };
    if (!isOwner && (!stagOwner || stagOwner.toLowerCase() !== address.toLowerCase())) {
      setMintResult("You don’t own this Stag!");
      return;
    }
    const amountInWei = BigInt(Math.floor(parseFloat(novenaAmount || '0') * 10**18));
    startNovenaFn({
      address: CONTRACT_ADDRESS,
      abi: contractABI,
      functionName: 'startNovena',
      chainId: baseSepolia.id,
      args: [BigInt(tokenId)],
      value: amountInWei,
    }, {
      onSuccess: async () => {
        setMintResult(`Novena started for Stag ID: ${tokenId}`);
        if (address) {
          fetchStagStatus(address);
          await fetch(`${API_URL}/api/start-novena`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ stagId: tokenId, ownerAddress: address, timezone, discordId, email: stagData[tokenId]?.email || '' }),
          });
        }
      },
      onError: (error) => setMintResult(`Failed to start novena: ${error.message}`),
    });
  };

  const handleCompleteNovena = (tokenId: number) => {
    if (!isConnected || !isOwner) return;
    const days = parseInt(batchDays[tokenId] || '0') || 0;
    if (days > 9) {
      setMintResult("Successful days cannot exceed 9");
      return;
    }
    completeNovenaFn({
      address: CONTRACT_ADDRESS,
      abi: contractABI,
      functionName: 'completeNovena',
      chainId: baseSepolia.id,
      args: [BigInt(tokenId), days],
    }, {
      onSuccess: () => {
        setMintResult(`Novena completed for Stag ID: ${tokenId}`);
        if (address) fetchStagStatus(address);
      },
      onError: (error) => setMintResult(`Failed to complete novena: ${error.message}`),
    });
  };

  const handleBatchComplete = () => {
    if (!isConnected || !isOwner) return;
    const stagIds = Object.keys(batchDays).map(id => BigInt(id));
    const successes = Object.values(batchDays).map(days => parseInt(days) || 0);
    if (stagIds.length === 0 || stagIds.length !== successes.length || successes.some(d => d > 9)) {
      setMintResult("Invalid batch data: ensure all Stag IDs have valid days (0-9)");
      return;
    }
    batchCompleteNovenaFn({
      address: CONTRACT_ADDRESS,
      abi: contractABI,
      functionName: 'batchCompleteNovena',
      chainId: baseSepolia.id,
      args: [stagIds, successes],
    }, {
      onSuccess: () => {
        setMintResult("Batch novena completion successful");
        if (address) fetchStagStatus(address);
        setBatchDays({});
      },
      onError: (error) => setMintResult(`Batch completion failed: ${error.message}`),
    });
  };

  const handleRefresh = () => {
    if (address) {
      fetchStagStatus(address);
      setMintResult("Status refreshed.");
    }
  };

  const handleDiscordLogin = () => {
    window.location.href = DISCORD_OAUTH_URL;
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setMintResult("Address copied to clipboard!");
  };

  if (!isMounted) {
    return <div>Loading...</div>;
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ margin: 0 }}>StagQuest {isOwner ? '(Admin)' : ''}</h1>
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
          <div style={{ marginBottom: '20px' }}>
            <label style={{ marginRight: '10px' }}>Mint Amount (ETH, min 0.0001):</label>
            <input
              type="number"
              step="0.0001"
              value={mintAmount}
              onChange={(e) => setMintAmount(e.target.value)}
              style={{ padding: '5px', borderRadius: '5px', border: '1px solid #ddd' }}
            />
            <button
              onClick={handleMint}
              disabled={mintPending}
              style={{
                padding: '10px 20px',
                backgroundColor: mintPending ? '#ccc' : '#0070f3',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: mintPending ? 'not-allowed' : 'pointer',
                marginLeft: '10px',
              }}
            >
              {mintPending ? 'Minting...' : 'Mint Stag'}
            </button>
          </div>
          {mintResult && <p style={{ color: mintResult.includes('failed') ? 'red' : 'green' }}>{mintResult}</p>}
          {mintError && <p style={{ color: 'red' }}>Mint Error: {mintError.message}</p>}
          {novenaError && <p style={{ color: 'red' }}>Novena Error: {novenaError.message}</p>}
          {completeError && <p style={{ color: 'red' }}>Complete Error: {completeError.message}</p>}
          {batchError && <p style={{ color: 'red' }}>Batch Error: {batchError.message}</p>}
          <h2>{isOwner ? 'All Stags' : 'Your Stags'}</h2>
          <button
            onClick={handleRefresh}
            style={{
              padding: '5px 10px',
              backgroundColor: '#ff9800',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              marginBottom: '10px',
            }}
          >
            Refresh Status
          </button>
          {isOwner && (
            <>
              <h3>Batch Complete Novenas</h3>
              <button
                onClick={handleBatchComplete}
                disabled={batchPending}
                style={{
                  padding: '5px 10px',
                  backgroundColor: batchPending ? '#ccc' : '#2196F3',
                  color: 'white',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: batchPending ? 'not-allowed' : 'pointer',
                  marginBottom: '10px',
                }}
              >
                {batchPending ? 'Completing...' : 'Batch Complete'}
              </button>
            </>
          )}
          {stags.length > 0 ? (
            stags.map((stag) => (
              <div key={stag.tokenId} style={{ border: '1px solid #ddd', padding: '10px', marginBottom: '10px', borderRadius: '5px' }}>
                <p>Stag ID: {stag.tokenId}</p>
                <p>
                  Owner: {stag.owner.slice(0, 6)}...{stag.owner.slice(-4)}
                  <button
                    onClick={() => copyToClipboard(stag.owner)}
                    style={{ marginLeft: '10px', padding: '2px 5px', backgroundColor: '#ddd', border: 'none', cursor: 'pointer' }}
                  >
                    📋
                  </button>
                </p>
                <p>Family Size: {stag.familySize}</p>
                <p>Active Novena: {stag.hasActiveNovena ? 'Yes' : 'No'}</p>
                <p>Successful Days: {stag.successfulDays}</p>
                {!stag.hasActiveNovena && (
                  <>
                    <div style={{ marginTop: '10px' }}>
                      <label style={{ marginRight: '10px' }}>Timezone:</label>
                      <input
                        type="text"
                        value={stagData[stag.tokenId]?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'}
                        onChange={(e) => setStagData({ ...stagData, [stag.tokenId]: { ...stagData[stag.tokenId], timezone: e.target.value, discordId: stagData[stag.tokenId]?.discordId || '', email: stagData[stag.tokenId]?.email || '', novenaAmount: stagData[stag.tokenId]?.novenaAmount || '0' } })}
                        style={{ padding: '5px', borderRadius: '5px', border: '1px solid #ddd', width: '150px' }}
                      />
                    </div>
                    <div style={{ marginTop: '10px' }}>
                      <label style={{ marginRight: '10px' }}>Discord ID:</label>
                      <input
                        type="text"
                        value={stagData[stag.tokenId]?.discordId || ''}
                        onChange={(e) => setStagData({ ...stagData, [stag.tokenId]: { ...stagData[stag.tokenId], discordId: e.target.value, timezone: stagData[stag.tokenId]?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC', email: stagData[stag.tokenId]?.email || '', novenaAmount: stagData[stag.tokenId]?.novenaAmount || '0' } })}
                        placeholder="e.g., 123456789012345678"
                        style={{ padding: '5px', borderRadius: '5px', border: '1px solid #ddd', width: '150px' }}
                      />
                    </div>
                    <div style={{ marginTop: '10px' }}>
                      <label style={{ marginRight: '10px' }}>Email:</label>
                      <input
                        type="email"
                        value={stagData[stag.tokenId]?.email || ''}
                        onChange={(e) => setStagData({ ...stagData, [stag.tokenId]: { ...stagData[stag.tokenId], email: e.target.value, timezone: stagData[stag.tokenId]?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC', discordId: stagData[stag.tokenId]?.discordId || '', novenaAmount: stagData[stag.tokenId]?.novenaAmount || '0' } })}
                        placeholder="e.g., user@example.com"
                        style={{ padding: '5px', borderRadius: '5px', border: '1px solid #ddd', width: '150px' }}
                      />
                    </div>
                    <div style={{ marginTop: '10px' }}>
                      <label style={{ marginRight: '10px' }}>Novena Amount (ETH, optional):</label>
                      <input
                        type="number"
                        step="0.0001"
                        value={stagData[stag.tokenId]?.novenaAmount || '0'}
                        onChange={(e) => setStagData({ ...stagData, [stag.tokenId]: { ...stagData[stag.tokenId], novenaAmount: e.target.value, timezone: stagData[stag.tokenId]?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC', discordId: stagData[stag.tokenId]?.discordId || '', email: stagData[stag.tokenId]?.email || '' } })}
                        style={{ padding: '5px', borderRadius: '5px', border: '1px solid #ddd', width: '100px' }}
                      />
                    </div>
                    <button
                      onClick={() => handleStartNovena(stag.tokenId)}
                      disabled={novenaPending}
                      style={{
                        padding: '5px 10px',
                        backgroundColor: novenaPending ? '#ccc' : '#4CAF50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: novenaPending ? 'not-allowed' : 'pointer',
                        marginTop: '10px',
                      }}
                    >
                      {novenaPending ? 'Starting...' : 'Start Novena'}
                    </button>
                  </>
                )}
                {isOwner && stag.hasActiveNovena && (
                  <>
                    <button
                      onClick={() => handleCompleteNovena(stag.tokenId)}
                      disabled={completePending}
                      style={{
                        padding: '5px 10px',
                        backgroundColor: completePending ? '#ccc' : '#F44336',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: completePending ? 'not-allowed' : 'pointer',
                        marginRight: '10px',
                      }}
                    >
                      {completePending ? 'Completing...' : 'Complete Novena'}
                    </button>
                    <div style={{ marginTop: '10px' }}>
                      <label style={{ marginRight: '10px' }}>How many successful days reported by the user? (0-9):</label>
                      <input
                        type="number"
                        min="0"
                        max="9"
                        value={batchDays[stag.tokenId] || '0'}
                        onChange={(e) => setBatchDays({ ...batchDays, [stag.tokenId]: e.target.value })}
                        style={{ padding: '5px', borderRadius: '5px', border: '1px solid #ddd', width: '50px' }}
                      />
                    </div>
                  </>
                )}
              </div>
            ))
          ) : (
            <p>No Stags found. Mint one to get started!</p>
          )}
        </main>
      ) : (
        <p>Please connect your wallet to continue.</p>
      )}
    </div>
  );
}