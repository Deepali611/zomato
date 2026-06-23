"use client";

import React, { useState, useEffect } from "react";

interface RecommendationItem {
  restaurant_id: string;
  rank: number;
  name: string;
  cuisines: string[];
  rating: number | null;
  cost_for_two: number | null;
  explanation: string;
  location: string;
}

interface ApiResponse {
  summary: string | null;
  recommendations: RecommendationItem[];
  degraded: boolean;
  warnings: string[];
}

const POPULAR_CUISINES = ["Italian", "Chinese", "South Indian"];
const LOCATIONS = [
  "Indiranagar",
  "BTM",
  "Jayanagar",
  "JP Nagar",
  "Koramangala 5th Block",
  "HSR",
  "MG Road",
  "Bandra West"
];

// Mock items to show on landing page before submit
const MOCK_RECOMMENDATIONS: RecommendationItem[] = [
  {
    restaurant_id: "mock-1",
    rank: 1,
    name: "The Aviary Rooftop",
    rating: 4.8,
    cuisines: ["Italian", "Fine Dining"],
    cost_for_two: 2500,
    location: "Indiranagar",
    explanation: "Unparalleled panoramic views combined with authentic wood-fired pizzas make this the perfect romantic escape you described."
  },
  {
    restaurant_id: "mock-2",
    rank: 2,
    name: "Lupa Italian",
    rating: 4.6,
    cuisines: ["Contemporary Italian", "Cocktails"],
    cost_for_two: 3000,
    location: "MG Road",
    explanation: "High-energy atmosphere with a specialized hand-crafted pasta menu that caters to your specific cuisine tag preferences."
  },
  {
    restaurant_id: "mock-3",
    rank: 3,
    name: "Bologna Bistro",
    rating: 4.5,
    cuisines: ["Classic Italian", "Wine Bar"],
    cost_for_two: 1800,
    location: "Indiranagar",
    explanation: "A hidden gem with dim lighting and excellent hospitality, providing the 'romantic' constraint in a more intimate setting."
  }
];

const MOCK_SUMMARY = `Based on your preference for <span class="text-[#c0c1ff] font-semibold">romantic rooftop</span> vibes and <span class="text-[#4edea3] font-semibold">Italian cuisine</span> in Indiranagar, I've curated a list of top-tier spots. Most of these venues are seeing peak activity tonight, so I recommend securing a reservation within the next 15 minutes.`;

const MOCK_CARD_IMAGES = [
  "https://lh3.googleusercontent.com/aida-public/AB6AXuD16t3b3NtGy7FN_Vaxe2VVA9pvdFVh1QwXB7XhoBq9MiXq7xAF3AOIFKixMF26Xnwp1llyCcjWoou7DECQcDd-L-w8odsXAAMKq_MYy-9fdlTx1aDyEhiuB8js5RFt90V6oGuVhh57RG_crqAXhu2V488z9WjOQdf9qmlsjPwYp7lQPxyWN5oZpCzPXW8bscLmEgZPE1QhSYZgF0ITyp9Rc-1f0_OZQ-TwjrthFdSZUGxzoWPaWOjLCX5sJqMkp1gGSBljdBFdfqo",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuC2ns28CkDvGT8btORKTmQqvQtbjo6SGYGCbN-CGTNj1tT0CKKNugFWoHV5W_MQ9Hfi0BLlyvNIxaGNAcHUzla6zCqIUilbJOGwwq4Irj1TIyqvaTGYdx5YQrpJUMsCYm35EdZIFfM3LPiEZPGo1n7tyKa19OclckdWbOhymaQdCScH-6doJfUzwz2r8RnuPLmc6g_r1SjCeu2MqLWuBclwMGsrPFcEovIOi3zJxx4rplzwbjFN8YpUZcqVnJGV1ceXr82AueI4a18",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuAtrFR9F_tERih7a2zJXRhYIg2Hel0mSV97KOxmqC1dKYRayaLa9Aoy_045OGqDOlNjTHHN_y1BCo4Zc7rn846wRLjrJfe2Ks2kaMhYpo4cDqBbX7LLUFehEvXwCYDWYAaj9jcb5E1UYKFkSoEy1ejLvBGBuT7zmDVEpT4EmXGa_PW7q2WTrJNYR_EONNiUN3qXHiEwIXmai-ZEzNxoH3QovsBsRefsOZaTyn7UnzrPwkLpCEfeu8k27GcInW8D3JHeHvHVqRuO46w"
];

export default function Home() {
  const [locations, setLocations] = useState<string[]>(LOCATIONS);
  const [location, setLocation] = useState("Indiranagar");
  const [budget, setBudget] = useState("medium");
  const [cuisineInput, setCuisineInput] = useState("Italian");
  const [minRating, setMinRating] = useState(4.0);
  const [additional, setAdditional] = useState("romantic rooftop");
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [summary, setSummary] = useState<string | null>(MOCK_SUMMARY);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>(MOCK_RECOMMENDATIONS);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [degraded, setDegraded] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/api/locations")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch locations");
        return res.json();
      })
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setLocations(data);
          // Auto-select the first location if current location is not in list
          if (!data.includes(location)) {
            setLocation(data[0]);
          }
        }
      })
      .catch((err) => {
        console.error("Error loading dynamic locations:", err);
      });
  }, []);

  // Split and clean cuisines from search inputs
  const activeCuisines = cuisineInput
    .split(",")
    .map((c) => c.trim())
    .filter(Boolean);

  const toggleCuisineTag = (tag: string) => {
    const lowerTags = activeCuisines.map((c) => c.toLowerCase());
    const idx = lowerTags.indexOf(tag.toLowerCase());
    
    let newTags: string[];
    if (idx > -1) {
      newTags = activeCuisines.filter((_, i) => i !== idx);
    } else {
      newTags = [...activeCuisines, tag];
    }
    setCuisineInput(newTags.join(", "));
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setWarnings([]);

    try {
      const response = await fetch("http://localhost:8000/api/recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          location,
          budget,
          cuisine: cuisineInput,
          min_rating: minRating,
          additional_preferences: additional.trim() || null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data: ApiResponse = await response.json();
      setSummary(data.summary);
      setRecommendations(data.recommendations);
      setWarnings(data.warnings);
      setDegraded(data.degraded);
    } catch (err: any) {
      setError(err.message || "Something went wrong. Is the API server running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen font-sans text-[#dfe2f1] bg-[#0f131d] overflow-x-hidden">
      {/* Background Decorative Radial Glows */}
      <div className="bg-glow-indigo"></div>
      <div className="bg-glow-emerald"></div>

      {/* Top Fixed Navigation Bar */}
      <nav className="fixed top-0 left-0 w-full h-[70px] z-50 flex justify-between items-center px-6 bg-[#0f131d]/75 backdrop-blur-xl border-b border-[#464554]/30">
        <div className="flex items-center gap-6">
          <span className="font-heading text-2xl font-bold text-[#dfe2f1] drop-shadow-[0_0_15px_rgba(192,193,255,0.5)]">
            🍽️ Zomato AI
          </span>
          <div className="flex gap-2">
            <div className="flex items-center gap-2 px-3 py-1 bg-[#1c1f2a] rounded-full border border-[#464554]/30">
              <span className="material-symbols-outlined text-[14px] text-[#c0c1ff]">memory</span>
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#c0c1ff]">
                Groq / Llama 3.3
              </span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 bg-[#1c1f2a] rounded-full border border-[#464554]/30">
              <span className="material-symbols-outlined text-[14px] text-[#4edea3]">database</span>
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#4edea3]">
                In-Memory Dataset
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="material-symbols-outlined text-[#c7c4d7] hover:text-[#c0c1ff] transition-colors cursor-pointer text-xl">
            notifications
          </span>
          <div className="w-10 h-10 rounded-full border-2 border-[#8083ff] overflow-hidden">
            <img
              alt="User Profile"
              className="w-full h-full object-cover"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuCO8c5rbiG4JWcz-GhcCd5UJ8lLKKUjxHvAvVh3yZkJ0C1TB_5n4dZ0rmBKcMVKcMoEBuxNXo4UWfaE7hVW_ThNIX27Tuld64KIVs9FSwVWE4h4S3n7OntsAL_1F45QIM4JAE4hFIC4rwWYihwBkh-FTniCZjZrkPs4CHn2tF0nk4uJup6DeGEGC2_yDYn7pXqyXV_u0OVYOlfdyKBE_ICrfJ41SIeZDLLbbphrva883Knq1oL5sNoV1hZgZsMDrLCdaLXqMGd1ct4"
            />
          </div>
        </div>
      </nav>

      {/* Main Container */}
      <div className="flex h-screen pt-[70px]">
        {/* Sidebar Controls */}
        <aside className="w-[380px] h-full p-6 flex flex-col space-y-8 bg-[#1c1f2a]/80 backdrop-blur-2xl border-r border-[#464554]/30 overflow-y-auto">
          <div className="space-y-2">
            <h2 className="font-heading text-2xl font-bold text-[#c0c1ff]">
              Concierge Search
            </h2>
            <p className="text-xs font-semibold text-[#c7c4d7]">
              AI-Powered Discovery
            </p>
          </div>

          <form onSubmit={handleGenerate} className="space-y-6">
            {/* Location dropdown */}
            <div className="space-y-2">
              <label className="text-[12px] font-bold uppercase tracking-wider text-[#c7c4d7]">
                Location
              </label>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#908fa0] text-xl pointer-events-none">
                  location_on
                </span>
                <select
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full bg-[#262a35] border border-[#464554]/40 rounded-xl py-3 pl-10 pr-4 appearance-none text-[#dfe2f1] focus:outline-none focus:border-[#c0c1ff] focus:ring-1 focus:ring-[#c0c1ff] transition-all"
                >
                  {locations.map((loc) => (
                    <option key={loc} value={loc}>
                      {loc}
                    </option>
                  ))}
                </select>
                <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-[#908fa0] text-xl pointer-events-none">
                  expand_more
                </span>
              </div>
            </div>

            {/* Budget segmented controls */}
            <div className="space-y-2">
              <label className="text-[12px] font-bold uppercase tracking-wider text-[#c7c4d7]">
                Budget Range
              </label>
              <div className="flex bg-[#0a0e18] p-1 rounded-xl border border-[#464554]/30 gap-1 w-full">
                {["low", "medium", "high"].map((tier) => {
                  const isActive = budget === tier;
                  return (
                    <button
                      key={tier}
                      type="button"
                      onClick={() => setBudget(tier)}
                      className={`flex-1 py-2 text-[12px] font-bold uppercase tracking-wider rounded-lg transition-all ${
                        isActive
                          ? "bg-[#4edea3]/15 border border-[#4edea3]/30 text-[#4edea3] shadow-[0_0_15px_rgba(78,222,163,0.2)]"
                          : "text-[#c7c4d7] hover:bg-[#353944] hover:text-[#dfe2f1]"
                      }`}
                    >
                      {tier}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Cuisines tag selector */}
            <div className="space-y-2">
              <label className="text-[12px] font-bold uppercase tracking-wider text-[#c7c4d7]">
                Cuisines
              </label>
              <input
                type="text"
                value={cuisineInput}
                onChange={(e) => setCuisineInput(e.target.value)}
                placeholder="Add cuisine..."
                className="w-full bg-[#262a35] border border-[#464554]/40 rounded-xl py-3 px-4 text-[#dfe2f1] focus:outline-none focus:border-[#c0c1ff] focus:ring-1 focus:ring-[#c0c1ff] transition-all"
              />
              <div className="flex flex-wrap gap-2 pt-2">
                {POPULAR_CUISINES.map((sug) => {
                  const isActive = activeCuisines.some(
                    (c) => c.toLowerCase() === sug.toLowerCase()
                  );
                  return (
                    <button
                      key={sug}
                      type="button"
                      onClick={() => toggleCuisineTag(sug)}
                      className={`px-3 py-1 rounded-full text-[12px] font-medium flex items-center gap-1 transition-all ${
                        isActive
                          ? "bg-[#c0c1ff]/10 border border-[#c0c1ff]/30 text-[#c0c1ff]"
                          : "bg-[#313540] border border-[#464554]/30 text-[#c7c4d7] hover:bg-[#353944]"
                      }`}
                    >
                      {sug}
                      {isActive && (
                        <span className="material-symbols-outlined text-[14px]">
                          close
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Minimum Rating Slider */}
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-[12px] font-bold uppercase tracking-wider text-[#c7c4d7]">
                  Minimum Rating
                </label>
                <span className="text-[#4edea3] font-bold text-sm">
                  {minRating.toFixed(1)}+
                </span>
              </div>
              <div className="relative pt-2">
                <input
                  type="range"
                  min="0.0"
                  max="5.0"
                  step="0.1"
                  value={minRating}
                  onChange={(e) => setMinRating(parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-gradient-to-r from-[#4edea3] to-[#c0c1ff] rounded-lg appearance-none cursor-pointer focus:outline-none accent-white"
                  style={{
                    boxShadow: "0 0 10px rgba(192, 193, 255, 0.4)",
                  }}
                />
                <div className="flex justify-between text-[10px] text-[#908fa0] px-1 pt-1 font-medium">
                  <span>0.0</span>
                  <span>2.5</span>
                  <span>5.0</span>
                </div>
              </div>
            </div>

            {/* Constraints */}
            <div className="space-y-2">
              <label className="text-[12px] font-bold uppercase tracking-wider text-[#c7c4d7]">
                Natural Language Constraints
              </label>
              <textarea
                value={additional}
                onChange={(e) => setAdditional(e.target.value)}
                placeholder="e.g. rooftop, romantic, live music, outdoor seating..."
                rows={3}
                className="w-full bg-[#262a35] border border-[#464554]/40 rounded-xl p-4 text-sm text-[#dfe2f1] resize-none focus:outline-none focus:border-[#c0c1ff] focus:ring-1 focus:ring-[#c0c1ff] transition-all"
              />
            </div>

            {/* Generate form submit button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-4 bg-[#00a572] text-[#00311f] font-heading font-semibold text-lg rounded-xl flex items-center justify-center gap-2 hover:scale-[1.02] active:scale-[0.98] transition-all shadow-[0_0_25px_rgba(78,222,163,0.3)] disabled:opacity-50"
            >
              <span className="material-symbols-outlined text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>
                auto_awesome
              </span>
              {loading ? "Generating..." : "Generate"}
            </button>
          </form>
        </aside>

        {/* Main Feed */}
        <main className="flex-1 h-full overflow-y-auto p-8 space-y-8">
          {/* Error Message */}
          {error && (
            <div className="glass-card p-4 rounded-xl border-l-4 border-red-400 bg-red-400/5 text-red-300 flex items-center gap-3">
              <span className="material-symbols-outlined text-xl">error</span>
              <span className="text-sm font-medium">{error}</span>
            </div>
          )}

          {/* Warnings List */}
          {warnings.length > 0 && (
            <div className="flex flex-col gap-3">
              {warnings.map((msg, idx) => (
                <div key={idx} className="glass-card p-4 rounded-xl border-l-4 border-[#ffb95f] bg-[#ffb95f]/5 text-[#ffb95f] flex items-center gap-3">
                  <span className="material-symbols-outlined text-xl">warning</span>
                  <span className="text-sm font-medium">{msg}</span>
                </div>
              ))}
            </div>
          )}

          {/* AI Narrative Summary */}
          {summary && (
            <section className="glass-card p-6 rounded-2xl border-l-4 border-[#c0c1ff] shadow-[0_0_20px_rgba(192,193,255,0.15)] mb-8">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-[#c0c1ff]/10 flex items-center justify-center flex-shrink-0">
                  <span className="material-symbols-outlined text-[#c0c1ff] text-3xl">chat_bubble</span>
                </div>
                <div className="space-y-2">
                  <h3 className="font-heading text-xl font-bold text-[#dfe2f1]">
                    AI Insights for your Evening
                  </h3>
                  <p
                    className="text-base text-[#c7c4d7] leading-relaxed"
                    dangerouslySetInnerHTML={{ __html: summary }}
                  />
                </div>
              </div>
            </section>
          )}

          {/* Empty State */}
          {!loading && recommendations.length === 0 && (
            <div className="glass-card p-8 rounded-2xl border-l-4 border-[#ffb4ab] bg-[#ffb4ab]/5 text-[#ffb4ab] text-center">
              <span className="material-symbols-outlined text-5xl mb-4">sentiment_dissatisfied</span>
              <h3 className="font-heading text-xl font-bold mb-2">No Match Found</h3>
              <p className="text-sm text-[#c7c4d7]">Try relaxing your rating or cuisine filters to discover more restaurants.</p>
            </div>
          )}

          {/* Results Grid */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
            {recommendations.map((item, idx) => {
              const imgUrl = MOCK_CARD_IMAGES[idx % MOCK_CARD_IMAGES.length];
              return (
                <div
                  key={item.restaurant_id}
                  className="glass-card rounded-2xl overflow-hidden hover:scale-[1.02] transition-all duration-300 group flex flex-col"
                >
                  <div className="relative h-48 overflow-hidden flex-shrink-0">
                    <img
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                      src={imgUrl}
                      alt={item.name}
                    />
                    <div className="absolute top-4 left-4 bg-[#0f131d]/85 backdrop-blur-md px-3 py-1 rounded-lg border border-[#464554]/30 flex items-center gap-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-[#c0c1ff]">
                        #{item.rank} Rank
                      </span>
                    </div>
                  </div>
                  <div className="p-6 space-y-4 flex flex-col flex-grow">
                    <div className="flex justify-between items-start gap-3">
                      <h4 className="font-heading text-lg font-bold text-[#dfe2f1] line-clamp-1">
                        {item.name}
                      </h4>
                      <div className="flex items-center gap-1 bg-[#00a572]/15 px-2 py-1 rounded-lg border border-[#00a572]/30 flex-shrink-0">
                        <span
                          className="material-symbols-outlined text-[#4edea3] text-[14px]"
                          style={{ fontVariationSettings: "'FILL' 1" }}
                        >
                          star
                        </span>
                        <span className="font-bold text-[#4edea3] text-sm">
                          {item.rating !== null ? item.rating.toFixed(1) : "N/A"}
                        </span>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {item.cuisines.map((c) => (
                        <span
                          key={c}
                          className="text-xs px-2 py-0.5 bg-[#313540] rounded border border-[#464554]/30 text-[#c7c4d7]"
                        >
                          {c}
                        </span>
                      ))}
                    </div>
                    <div className="flex justify-between items-center text-sm font-medium">
                      <span className="text-[#c7c4d7]">
                        {item.cost_for_two !== null
                          ? `₹${item.cost_for_two.toLocaleString()} for two`
                          : "Cost not available"}
                      </span>
                      <span className="text-[#908fa0]">{item.location}</span>
                    </div>
                    <div className="p-3 bg-[#00a572]/5 border-l-4 border-[#4edea3] rounded-r-lg mt-auto">
                      <p className="text-sm italic text-[#c7c4d7]">
                        &quot;Why this fits: {item.explanation}&quot;
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* More Results CTA */}
          {recommendations.length > 0 && (
            <div className="flex justify-center pt-8">
              <button className="px-8 py-3 rounded-full border border-[#464554]/30 text-[#c7c4d7] hover:bg-[#353944] hover:text-[#c0c1ff] transition-all flex items-center gap-2 bg-transparent cursor-pointer font-medium text-sm">
                <span className="material-symbols-outlined">expand_more</span>
                <span>Discover More Matches</span>
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
