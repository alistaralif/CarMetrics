import Link from "next/link";

export default function Hero() {
  return (
    <section className="hero">
      <div className="hero-text">
        <h1>CarMetrics</h1>
        <div className="hero-subtitle">
          {/* <p>
              Analyze used car listings instantly.
              Compare depreciation, loan cost, and value — all in one place.
          </p>       */}
          <p>
            Depreciation. Financing at today's rates. Power-to-weight ratios. 
            Everything you need to compare used cars — calculated instantly. 
            Check out the example below.
          </p>
        </div>
        </div>
      <Link href="/quick-start" className="hero-cta">
          Get Started →
        </Link>
        {/* <br /> */}
      


    </section>
  );
}