'use client';

import React, { useState, useEffect } from 'react';
import { ConnectWallet } from '@coinbase/onchainkit/wallet';
import { useAccount, useWriteContract } from 'wagmi';
import { baseSepolia } from 'wagmi/chains';
import contractABI from '../data/abi.json';

const CONTRACT_ADDRESS = '0x5E1557B4C7Fc5268512E98662F23F923042FF5c5';
const MINIMUM_MINT_AMOUNT = BigInt('100000000000000'); // 0.0001 ETH

export default function Home() {
  const { address, isConnected } = useAccount();
  const [mintResult, setMintResult] = useState<string | null>(null);
  const [stags, setStags] = useState<any[]>([]);
  const [isMounted, setIsMounted] = useState(false);
  const [mintAmount, setMintAmount] = useState<string>('0.0001');

  const API_URL = 'https://stag-quest.vercel.app';

  const { writeContract: mintStag, isPending: mintPending, error: mintError } = useWriteContract();
  const { writeContract: startNovenaFn, isPending: novenaPending, error: novenaError } = useWriteContract();

  useEffect(() => {
    setIsMounted(true);
    if (address) {
      fetchStagStatus(address);
    }
  }, [address]);

  async function fetchStagStatus(address: string) {
    try {
      const response = await fetch(`${API_URL}/api/status`);
      const text = await response.text();
      if (!response.ok) throw new Error(`Server error: ${response.status} - ${text}`);
      const data = JSON.parse(text);
      if (data.stags) {
        const userStags = data.stags.filter((stag: any) => stag.owner.toLowerCase() === address.toLowerCase());
        setStags(userStags);
      } else {
        setMintResult("No stags found in response.");
      }
    } catch (error: any) {
      console.error('Status error:', error);
      setMintResult(`Failed to fetch status: ${error.message}`);
    }
  }

  const handleMint = () => {
    if (!isConnected) {
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

  const handleStartNovena = (tokenId: number) => {
    if (!isConnected) {
      setMintResult("Please connect your wallet first.");
      return;
    }
    startNovenaFn({
      address: CONTRACT_ADDRESS,
      abi: contractABI,
      functionName: 'startNovena',
      chainId: baseSepolia.id,
      args: [BigInt(tokenId)],
    }, {
      onSuccess: () => {
        setMintResult(`Novena started for Stag ID: ${tokenId}`);
        if (address) fetchStagStatus(address);
      },
      onError: (error) => setMintResult(`Failed to start novena: ${error.message}`),
    });
  };

  if (!isMounted) {
    return <div>Loading...</div>;
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ margin: 0 }}>StagQuest</h1>
        <ConnectWallet 
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 min-w-[150px] text-center"
          text={isConnected ? `Connected: ${address?.slice(0, 6)}...${address?.slice(-4)}` : 'Connect Wallet'}
        />
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
          <h2>Your Stags</h2>
          {stags.length > 0 ? (
            stags.map((stag) => (
              <div key={stag.tokenId} style={{ border: '1px solid #ddd', padding: '10px', marginBottom: '10px', borderRadius: '5px' }}>
                <p>Stag ID: {stag.tokenId}</p>
                <p>Family Size: {stag.familySize}</p>
                <p>Active Novena: {stag.hasActiveNovena ? 'Yes' : 'No'}</p>
                <p>Successful Days: {stag.successfulDays}</p>
                {!stag.hasActiveNovena && (
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
                    }}
                  >
                    {novenaPending ? 'Starting...' : 'Start Novena'}
                  </button>
                )}
                {novenaError && <p style={{ color: 'red' }}>Novena Error: {novenaError.message}</p>}
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