'use client';

import React, { useState, useEffect } from 'react';
import { Wallet, ConnectWallet, WalletDropdown, WalletDropdownDisconnect } from '@coinbase/onchainkit/wallet';
import { useAccount } from 'wagmi';

export default function Home() {
  const { address } = useAccount();
  const [mintResult, setMintResult] = useState<string | null>(null);
  const [stags, setStags] = useState<any[]>([]);
  const [isMounted, setIsMounted] = useState(false);
  const [isWalletOpen, setIsWalletOpen] = useState(false);

  const API_URL = 'https://stag-quest.vercel.app';

  useEffect(() => {
    setIsMounted(true);
    if (address) {
      fetchStagStatus(address);
    }
  }, [address]);

  async function mintStag() {
    if (!address) {
      setMintResult("Please connect your wallet first.");
      return;
    }
    try {
      const response = await fetch(`${API_URL}/api/mint`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount: '0.0001', address })
      });
      const text = await response.text();
      if (!response.ok) throw new Error(`Server error: ${response.status} - ${text}`);
      const data = JSON.parse(text);
      setMintResult(data.tokenId ? `Stag minted! Token ID: ${data.tokenId}` : `Minting failed: ${data.error}`);
      fetchStagStatus(address);
    } catch (error: any) {
      console.error('Mint error:', error);
      setMintResult(`Minting failed: ${error.message}`);
    }
  }

  async function startNovena(tokenId: number) {
    if (!address) {
      setMintResult("Please connect your wallet first.");
      return;
    }
    try {
      const response = await fetch(`${API_URL}/api/novena`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stagId: tokenId, amount: '0', address })
      });
      const text = await response.text();
      if (!response.ok) throw new Error(`Server error: ${response.status} - ${text}`);
      const data = JSON.parse(text);
      setMintResult(data.message || `Failed to start novena: ${data.error}`);
      fetchStagStatus(address);
    } catch (error: any) {
      console.error('Novena error:', error);
      setMintResult(`Failed to start novena: ${error.message}`);
    }
  }

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

  if (!isMounted) {
    return <div>Loading...</div>;
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ margin: 0 }}>StagQuest</h1>
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setIsWalletOpen(!isWalletOpen)}
            style={{
              padding: '10px 20px',
              borderRadius: '9999px',
              backgroundColor: address ? '#4CAF50' : '#0070f3',
              color: 'white',
              border: 'none',
              cursor: 'pointer',
              fontSize: '16px',
            }}
          >
            {address ? `Connected: ${address.slice(0, 6)}...${address.slice(-4)}` : 'Connect Wallet'}
          </button>
          {isWalletOpen && (
            <div
              style={{
                position: 'absolute',
                top: '100%',
                right: 0,
                backgroundColor: 'white',
                border: '1px solid #ddd',
                borderRadius: '8px',
                padding: '10px',
                boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                zIndex: 10,
              }}
            >
              <Wallet>
                <ConnectWallet />
                {address && <WalletDropdownDisconnect />}
              </Wallet>
            </div>
          )}
        </div>
      </header>
      {address ? (
        <main>
          <button
            onClick={mintStag}
            style={{
              padding: '10px 20px',
              backgroundColor: '#0070f3',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              marginBottom: '20px',
            }}
          >
            Mint Stag
          </button>
          {mintResult && <p style={{ color: mintResult.includes('failed') ? 'red' : 'green' }}>{mintResult}</p>}
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
                    onClick={() => startNovena(stag.tokenId)}
                    style={{
                      padding: '5px 10px',
                      backgroundColor: '#4CAF50',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      cursor: 'pointer',
                    }}
                  >
                    Start Novena
                  </button>
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