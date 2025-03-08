'use client';

import React, { useState, useEffect } from 'react';
import { Wallet, ConnectWallet, WalletDropdown, WalletDropdownDisconnect } from '@coinbase/onchainkit/wallet';
import { useAccount } from 'wagmi';

export default function Home() {
  const { address } = useAccount();
  const [mintResult, setMintResult] = useState<string | null>(null);
  const [stags, setStags] = useState<any[]>([]);
  const [isMounted, setIsMounted] = useState(false);

  const API_URL = 'https://stag-quest.vercel.app';

  useEffect(() => {
    setIsMounted(true); // Ensure client-side rendering
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
      if (!response.ok) throw new Error(`Server error: ${response.status} - ${await response.text()}`);
      const data = await response.json();
      setMintResult(data.tokenId ? `Stag minted! Token ID: ${data.tokenId}` : `Minting failed: ${data.error}`);
      fetchStagStatus(address);
    } catch (error: any) {
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
      if (!response.ok) throw new Error(`Server error: ${response.status} - ${await response.text()}`);
      const data = await response.json();
      setMintResult(data.message || `Failed to start novena: ${data.error}`);
      fetchStagStatus(address);
    } catch (error: any) {
      setMintResult(`Failed to start novena: ${error.message}`);
    }
  }

  async function fetchStagStatus(address: string) {
    try {
      const response = await fetch(`${API_URL}/api/status`);
      if (!response.ok) throw new Error(`Server error: ${response.status} - ${await response.text()}`);
      const data = await response.json();
      if (data.stags) {
        const userStags = data.stags.filter((stag: any) => stag.owner.toLowerCase() === address.toLowerCase());
        setStags(userStags);
      } else {
        setMintResult("No stags found in response.");
      }
    } catch (error: any) {
      setMintResult(`Failed to fetch status: ${error.message}`);
    }
  }

  if (!isMounted) {
    return <div>Loading...</div>; // Prevent hydration mismatch
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>StagQuest</h1>
      <Wallet>
        <ConnectWallet />
        {address && (
          <WalletDropdown>
            <WalletDropdownDisconnect />
          </WalletDropdown>
        )}
      </Wallet>
      {address ? (
        <>
          <p>Connected as: {address}</p>
          <button onClick={mintStag}>Mint Stag</button>
          {mintResult && <p>{mintResult}</p>}
          <h2>Your Stags</h2>
          {stags.length > 0 ? (
            stags.map((stag) => (
              <div key={stag.tokenId}>
                <p>Stag ID: {stag.tokenId}</p>
                <p>Family Size: {stag.familySize}</p>
                <p>Active Novena: {stag.hasActiveNovena ? 'Yes' : 'No'}</p>
                <p>Successful Days: {stag.successfulDays}</p>
                {!stag.hasActiveNovena && (
                  <button onClick={() => startNovena(stag.tokenId)}>Start Novena</button>
                )}
                <hr />
              </div>
            ))
          ) : (
            <p>No Stags found. Mint one to get started!</p>
          )}
        </>
      ) : (
        <p>Please connect your wallet to continue.</p>
      )}
    </div>
  );
}