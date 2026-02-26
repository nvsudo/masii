interface CategoryCardProps {
  emoji: string
  name: string
  promptCount: number
  avgRating: number
  active?: boolean
  onClick?: () => void
}

export default function CategoryCard({
  emoji,
  name,
  promptCount,
  avgRating,
  active = false,
  onClick,
}: CategoryCardProps) {
  void avgRating

  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={[
        'glass-card glass-interactive w-full text-left p-5 sm:p-6',
        active ? 'ring-1 ring-[#FFD700]/60 border-[#FFD700]/30 bg-white/10' : '',
      ].join(' ')}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-2xl sm:text-3xl" aria-hidden="true">
            {emoji}
          </div>
          <h3 className="mt-3 text-base sm:text-lg font-semibold text-white leading-snug">
            {name}
          </h3>
        </div>
        {active ? (
          <span className="text-xs font-medium text-[#FFD700]">Active</span>
        ) : null}
      </div>

      <div className="mt-5 flex items-center justify-between text-sm">
        <span className="text-[#D0D0D0]">{promptCount} prompts</span>
        {/* <span className="text-[#FFD700]">★ {avgRating.toFixed(1)}</span> */}
      </div>
    </button>
  )
}
