type PageHeroProps = {
  eyebrow: string;
  title: string;
  lead: string;
  className?: string;
};

export function PageHero({ eyebrow, title, lead, className = "" }: PageHeroProps) {
  return (
    <section className={`mb-10 ${className}`}>
      <p className="nf-eyebrow">{eyebrow}</p>
      <h1 className="mt-2 font-serif text-3xl font-semibold tracking-tight text-text sm:text-4xl">
        {title}
      </h1>
      <p className="mt-3 max-w-2xl text-base leading-relaxed text-muted">{lead}</p>
    </section>
  );
}
