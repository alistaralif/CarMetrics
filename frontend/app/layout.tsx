import "./globals.css";

import Navbar from "@/components/Navbar";
import { ResultsProvider } from "@/context/ResultsContext";
import ClientProviders from "@/components/ClientProviders";
import Footer from "@/components/Footer";
import RouteTransition from "@/components/RouteTransition";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" data-scroll-behavior="smooth">
      <body>
        <ClientProviders>
          <ResultsProvider>
            <Navbar />
              <RouteTransition>
                {children}
              </RouteTransition>
            <Footer />
          </ResultsProvider>
        </ClientProviders>
      </body>
    </html>
  );
}
