'use client';

import React, { useState } from 'react';
import { ethers } from 'ethers';

export default function Home() {
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [mintResult, setMintResult] = useState<string | null>(null);
  const [stags, setStags] = useState<any[]>([]);
  const [selectedWallet, setSelectedWallet] = useState<string>('metamask');

  const API_URL = 'https://stag-quest.vercel.app';

  async function connectWallet(walletType: string) {
    if (typeof window.ethereum === 'undefined') {
      alert("No wallet detected. Please install MetaMask or Coinbase Wallet.");
      return;
    }

    let provider: ethers.BrowserProvider;
    try {
      const ethereum = window.ethereum;

      // Detect available wallets
      const isMetaMask = ethereum.isMetaMask;
      const isCoinbaseWallet = ethereum.isCoinbaseWallet || ethereum.providers?.some((p: any) => p.isCoinbaseWallet);

      if (walletType === 'metamask') {
        if (!isMetaMask) {
          alert("MetaMask not detected. Please ensure it’s installed and enabled.");
          return;
        }
        provider = new ethers.BrowserProvider(
          ethereum.providers ? ethereum.providers.find((p: any) => p.isMetaMask) || ethereum : ethereum
        );
      } else if (walletType === 'coinbase') {
        if (!isCoinbaseWallet) {
          alert("Coinbase Wallet not detected. Please ensure it’s installed and enabled.");
          return;
        }
        provider = new ethers.BrowserProvider(
          ethereum.providers ? ethereum.providers.find((p: any) => p.isCoinbaseWallet) || ethereum : ethereum
        );
      } else {
        alert("Invalid wallet selection.");
        return;
      }

      // Request accounts and get signer
      await provider.send("eth_requestAccounts", []);
      const signer = await provider.getSigner(); // Await the signer
      const address = await signer.getAddress(); // Should now work
      setWalletAddress(address);
      fetchStagStatus(address);
    } catch (error: any) {
      if (error.code === 4001) {
        setMintResult(`Connection to ${walletType} wallet cancelled by user.`);
      } else {
        console.error(`Failed to connect ${walletType} wallet:`, error);
        setMintResult(`Failed to connect ${walletType} wallet: ${error.message || 'Unknown error'}`);
      }
    }
  }

  async function mintStag() {
    if (!walletAddress) {
      alert("Please connect your wallet first.");
      return;
    }
    try {
      const response = await fetch(`${API_URL}/api/mint`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount: '0.0001', address: walletAddress })
      });
      const data = await response.json();
      if (data.tokenId) {
        setMintResult(`Stag minted! Token ID: ${data.tokenId}`);
        fetchStagStatus(walletAddress);
      } else {
        setMintResult(`Minting failed: ${data.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Minting failed:', error);
      setMintResult('Minting failed.');
    }
  }

  async function startNovena(tokenId: number) {
    if (!walletAddress) {
      alert("Please connect your wallet first.");
      return;
    }
    try {
      const response = await fetch(`${API_URL}/api/novena`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stagId: tokenId, amount: '0', address: walletAddress })
      });
      const data = await response.json();
      if (data.message) {
        setMintResult(data.message);
        fetchStagStatus(walletAddress);
      } else {
        setMintResult(`Failed to start novena: ${data.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Novena start failed:', error);
      setMintResult('Failed to start novena.');
    }
  }

  async function fetchStagStatus(address: string) {
    try {
      const response = await fetch(`${API_URL}/api/status`);
      const data = await response.json();
      if (data.stags) {
        const userStags = data.stags.filter(
          (stag: any) => stag.owner.toLowerCase() === address.toLowerCase()
        );
        setStags(userStags);
      }
    } catch (error) {
      console.error('Failed to fetch status:', error);
    }
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>StagQuest</h1>
      {walletAddress ? (
        <>
          <p>Connected as: {walletAddress}</p>
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
                  <button onClick={() => startNovena(stag.tokenId)}>
                    Start Novena
                  </button>
                )}
                <hr />
              </div>
            ))
          ) : (
            <p>No Stags found. Mint one to get started!</p>
          )}
        </>
      ) : (
        <div>
          <label>Select Wallet: </label>
          <select
            value={selectedWallet}
            onChange={(e) => setSelectedWallet(e.target.value)}
          >
            <option value="metamask">MetaMask</option>
            <option value="coinbase">Coinbase Wallet</option>
          </select>
          <button onClick={() => connectWallet(selectedWallet)}>
            Connect {selectedWallet === 'metamask' ? 'MetaMask' : 'Coinbase Wallet'}
          </button>
          {mintResult && <p>{mintResult}</p>}
        </div>
      )}
    </div>
  );
}