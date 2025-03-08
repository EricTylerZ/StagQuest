'use client';

import { OnchainKitProvider } from '@coinbase/onchainkit';
import { baseSepolia } from 'wagmi/chains';
import { WagmiProvider, createConfig, http } from 'wagmi';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const config = createConfig({
  chains: [baseSepolia],
  transports: { [baseSepolia.id]: http('https://sepolia.base.org') }
});

const queryClient = new QueryClient();

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <WagmiProvider config={config}>
          <QueryClientProvider client={queryClient}>
            <OnchainKitProvider chain={baseSepolia}>
              {children}
            </OnchainKitProvider>
          </QueryClientProvider>
        </WagmiProvider>
      </body>
    </html>
  );
}