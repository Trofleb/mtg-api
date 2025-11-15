import { CardSearch } from "@/components/card-search";

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Magic the Gathering Card Search</h1>
          <p className="text-muted-foreground">
            Card info comes from the{" "}
            <a
              href="https://scryfall.com/docs/api"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              Scryfall API
            </a>
            . Thank you so much for all the data!
          </p>
        </header>
        <CardSearch />
      </div>
    </main>
  );
}
