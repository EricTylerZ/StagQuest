'use client';

import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';

// Replace with your actual contract address if different
const CONTRACT_ADDRESS = '0x5E1557B4C7Fc5268512E98662F23F923042FF5c5';

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

// Using your provided Discord OAuth URL
const DISCORD_OAUTH_URL = 'https://discord.com/oauth2/authorize?client_id=1348188422367477842&redirect_uri=https%3A%2F%2Fstag-quest.vercel.app%2Fapi%2Fdiscord-callback&response_type=code&scope=identify';

// Define stag type
interface Stag {
  tokenId: number;
  owner: string;
  familySize: number;
  hasActiveNovena: boolean;
  successfulDays: number;
}

export default function Home() {
  const [provider, setProvider] = useState<ethers.BrowserProvider | null>(null);
  const [signer, setSigner] = useState<ethers.JsonRpcSigner | null>(null);
  const [contract, setContract] = useState<ethers.Contract | null>(null);
  const [address, setAddress] = useState<string>('');
  const [isOwner, setIsOwner] = useState<boolean>(false);
  const [stags, setStags] = useState<Stag[]>([]);
  const [mintAmount, setMintAmount] = useState<string>('0.0001');
  const [novenaAmount, setNovenaAmount] = useState<string>('0.0001');
  const [successfulDays, setSuccessfulDays] = useState<{ [key: number]: string }>({});
  const [batchStagIds, setBatchStagIds] = useState<string>('');
  const [batchSuccesses, setBatchSuccesses] = useState<string>('');

  // Initialize wallet connection and fetch stags
  useEffect(() => {
    const init = async () => {
      if (!window.ethereum) {
        alert('Please install MetaMask or another web3 wallet.');
        return;
      }
      try {
        await window.ethereum.request({ method: 'eth_requestAccounts' });
        const provider = new ethers.BrowserProvider(window.ethereum);
        const signer = await provider.getSigner();
        const address = await signer.getAddress();
        const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer);

        setProvider(provider);
        setSigner(signer);
        setAddress(address);
        setContract(contract);

        const owner = await contract.owner();
        setIsOwner(address.toLowerCase() === owner.toLowerCase());

        await fetchStagStatuses(contract, address, isOwner);
      } catch (error) {
        console.error('Wallet connection failed:', error);
        alert('Failed to connect wallet.');
      }
    };
    init();
  }, []);

  // Fetch all stag details
  const fetchStagStatuses = async (contract: ethers.Contract, address: string, isOwner: boolean) => {
    try {
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

  // Mint a new stag
  const handleMintStag = async () => {
    if (!contract) return;
    try {
      const weiAmount = ethers.parseEther(mintAmount);
      const tx = await contract.mintStag({ value: weiAmount });
      await tx.wait();
      alert('Stag minted successfully!');
      await fetchStagStatuses(contract, address, isOwner);
    } catch (error) {
      console.error('Mint failed:', error);
      alert('Minting failed.');
    }
  };

  // Start a novena and notify backend for Discord prompts
  const handleStartNovena = async (stagId: number) => {
    if (!contract) return;
    try {
      const weiAmount = ethers.parseEther(novenaAmount);
      const tx = await contract.startNovena(stagId, { value: weiAmount });
      await tx.wait();
      alert('Novena started successfully!');

      // Notify backend to start Discord prompts
      await fetch('/api/start-novena', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stagId, ownerAddress: address }),
      });

      await fetchStagStatuses(contract, address, isOwner);
    } catch (error) {
      console.error('Novena start failed:', error);
      alert('Failed to start novena.');
    }
  };

  // Complete a novena (admin only)
  const handleCompleteNovena = async (stagId: number) => {
    if (!contract || !isOwner) return;
    const days = parseInt(successfulDays[stagId] || '0');
    if (isNaN(days) || days < 0 || days > 9) {
      alert('Successful days must be between 0 and 9.');
      return;
    }
    try {
      const tx = await contract.completeNovena(stagId, days);
      await tx.wait();
      alert('Novena completed successfully!');
      await fetchStagStatuses(contract, address, isOwner);
    } catch (error) {
      console.error('Completion failed:', error);
      alert('Failed to complete novena.');
    }
  };

  // Batch complete novenas (admin only)
  const handleBatchCompleteNovena = async () => {
    if (!contract || !isOwner) return;
    const stagIds = batchStagIds.split(',').map(id => parseInt(id.trim()));
    const successes = batchSuccesses.split(',').map(s => parseInt(s.trim()));
    if (stagIds.length !== successes.length || stagIds.some(isNaN) || successes.some(s => s < 0 || s > 9)) {
      alert('Invalid batch data: check stag IDs and successful days (0-9).');
      return;
    }
    try {
      const tx = await contract.batchCompleteNovena(stagIds, successes);
      await tx.wait();
      alert('Batch completed successfully!');
      await fetchStagStatuses(contract, address, isOwner);
    } catch (error) {
      console.error('Batch failed:', error);
      alert('Batch completion failed.');
    }
  };

  // Discord login redirect
  const handleDiscordLogin = () => {
    window.location.href = DISCORD_OAUTH_URL;
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>StagQuest {isOwner ? '(Admin)' : ''}</h1>
        <button onClick={handleDiscordLogin}>Login with Discord</button>
      </header>

      {address ? (
        <main>
          {/* Mint Section */}
          <div style={{ marginBottom: '20px' }}>
            <h2>Mint a Stag</h2>
            <input
              type="number"
              step="0.0001"
              value={mintAmount}
              onChange={(e) => setMintAmount(e.target.value)}
              placeholder="Amount in ETH"
              style={{ marginRight: '10px' }}
            />
            <button onClick={handleMintStag}>Mint Stag</button>
          </div>

          {/* Stag List */}
          <h2>{isOwner ? 'All Stags' : 'Your Stags'}</h2>
          {stags.length > 0 ? (
            stags.map((stag) => (
              <div key={stag.tokenId} style={{ border: '1px solid #ddd', padding: '10px', marginBottom: '10px' }}>
                <p><strong>Stag ID:</strong> {stag.tokenId}</p>
                <p><strong>Owner:</strong> {stag.owner}</p>
                <p><strong>Family Size:</strong> {stag.familySize}</p>
                <p><strong>Active Novena:</strong> {stag.hasActiveNovena ? 'Yes' : 'No'}</p>
                <p><strong>Successful Days:</strong> {stag.successfulDays}</p>

                {!stag.hasActiveNovena && (
                  <>
                    <input
                      type="number"
                      step="0.0001"
                      value={novenaAmount}
                      onChange={(e) => setNovenaAmount(e.target.value)}
                      placeholder="Amount in ETH"
                      style={{ marginRight: '10px' }}
                    />
                    <button onClick={() => handleStartNovena(stag.tokenId)}>Start Novena</button>
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
                    <button onClick={() => handleCompleteNovena(stag.tokenId)}>Complete Novena</button>
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
              <button onClick={handleBatchCompleteNovena}>Batch Complete</button>
            </div>
          )}
        </main>
      ) : (
        <p>Please connect your wallet to continue.</p>
      )}
    </div>
  );
}