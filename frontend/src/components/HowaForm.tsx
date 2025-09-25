import { useState } from "react";

interface HowaFormProps {
  onSubmit: (theme: string, audiences: ("子供" | "若者" | "ビジネスパーソン" | "高齢者" | "指定なし")[]) => Promise<void>;
  isLoading: boolean;
}

const audienceOptions = [
  { value: "子供", label: "子供" },
  { value: "若者", label: "若者" },
  { value: "ビジネスパーソン", label: "ビジネスパーソン" },
  { value: "高齢者", label: "高齢者" },
  { value: "指定なし", label: "指定なし" },
];

export function HowaForm({ onSubmit, isLoading }: HowaFormProps) {
  const [theme, setTheme] = useState<string>("");
  const [selectedAudiences, setSelectedAudiences] = useState<("子供" | "若者" | "ビジネスパーソン" | "高齢者" | "指定なし")[]>(["指定なし"]);

  const handleAudienceChange = (audience: "子供" | "若者" | "ビジネスパーソン" | "高齢者" | "指定なし", checked: boolean) => {
    if (checked) {
      setSelectedAudiences(prev => [...prev, audience]);
    } else {
      setSelectedAudiences(prev => prev.filter(a => a !== audience));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (theme.trim() && selectedAudiences.length > 0) {
      onSubmit(theme.trim(), selectedAudiences);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
      <div style={{ marginBottom: '16px' }}>
        <label htmlFor="theme" style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          法話のテーマ:
        </label>
        <input
          id="theme"
          type="text"
          value={theme}
          onChange={(e) => setTheme(e.target.value)}
          placeholder="例: 感謝の心"
          required
          style={{
            width: '100%',
            padding: '8px',
            fontSize: '16px',
            border: '1px solid #ccc',
            borderRadius: '4px'
          }}
        />
      </div>

      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          対象者 (複数選択可):
        </label>
        {audienceOptions.map((option) => (
          <label key={option.value} style={{ display: 'block', marginBottom: '4px' }}>
            <input
              type="checkbox"
              checked={selectedAudiences.includes(option.value)}
              onChange={(e) => handleAudienceChange(option.value, e.target.checked)}
              style={{ marginRight: '8px' }}
            />
            {option.label}
          </label>
        ))}
      </div>

      <button
        type="submit"
        disabled={isLoading || !theme.trim() || selectedAudiences.length === 0}
        style={{
          padding: '12px 24px',
          fontSize: '16px',
          backgroundColor: isLoading ? '#ccc' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: isLoading ? 'not-allowed' : 'pointer'
        }}
      >
        {isLoading ? "生成中..." : "法話を生成"}
      </button>
    </form>
  );
}