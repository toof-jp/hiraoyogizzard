import { useState } from "react";

type Audience = "子供" | "若者" | "ビジネスパーソン" | "高齢者" | "指定なし";

interface HowaFormProps {
  onSubmit: (theme: string, audiences: Audience[]) => Promise<void>;
  isLoading: boolean;
}

const audienceOptions: { value: Audience; label: string }[] = [
  { value: "子供", label: "子供" },
  { value: "若者", label: "若者" },
  { value: "ビジネスパーソン", label: "ビジネスパーソン" },
  { value: "高齢者", label: "高齢者" },
  { value: "指定なし", label: "指定なし" },
];

export function HowaForm({ onSubmit, isLoading }: HowaFormProps) {
  const [theme, setTheme] = useState<string>("");
  const [selectedAudiences, setSelectedAudiences] = useState<Audience[]>([
    "指定なし",
  ]);

  const handleAudienceChange = (audience: Audience, checked: boolean) => {
    if (checked) {
      if (audience === "指定なし") {
        // 「指定なし」を選択した場合、他の選択をすべて解除
        setSelectedAudiences(["指定なし"]);
      } else {
        // 他の選択肢を選択した場合、「指定なし」を解除してから追加
        setSelectedAudiences((prev) => {
          const withoutUnspecified = prev.filter((a) => a !== "指定なし");
          return [...withoutUnspecified, audience];
        });
      }
    } else {
      setSelectedAudiences((prev) => prev.filter((a) => a !== audience));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!theme.trim()) {
      alert("法話のテーマを入力してください");
      return;
    }

    if (selectedAudiences.length === 0) {
      alert("対象者を選択してください");
      return;
    }

    onSubmit(theme.trim(), selectedAudiences);
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "20px" }}>
      <div style={{ marginBottom: "16px" }}>
        <label
          htmlFor="theme"
          style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}
        >
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
            width: "100%",
            padding: "8px",
            fontSize: "16px",
            border: "1px solid #ccc",
            borderRadius: "4px",
          }}
        />
      </div>

      <div style={{ marginBottom: "16px" }}>
        <label
          style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}
        >
          対象者 (複数選択可):
        </label>
        {audienceOptions.map((option) => (
          <label
            key={option.value}
            style={{ display: "block", marginBottom: "4px" }}
          >
            <input
              type="checkbox"
              checked={selectedAudiences.includes(option.value)}
              onChange={(e) =>
                handleAudienceChange(option.value, e.target.checked)
              }
              style={{ marginRight: "8px" }}
            />
            {option.label}
          </label>
        ))}
      </div>

      <button
        type="submit"
        disabled={isLoading}
        style={{
          padding: "16px 32px",
          fontSize: "16px",
          fontWeight: "500",
          fontFamily: '"Noto Serif JP", serif',
          background: isLoading ? "linear-gradient(135deg, #cbd5e0 0%, #a0aec0 100%)" : "linear-gradient(135deg, #6a9cb6 0%, #5a8ca0 100%)",
          color: "white",
          border: "1px solid rgba(255, 255, 255, 0.2)",
          borderRadius: "8px",
          cursor: isLoading ? "not-allowed" : "pointer",
          transition: "all 0.3s ease",
          boxShadow: isLoading ? "none" : "0 4px 15px rgba(106, 156, 182, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2)",
          letterSpacing: "0.02em",
          position: "relative",
          overflow: "hidden",
        }}
        onMouseEnter={(e) => {
          if (!isLoading) {
            e.currentTarget.style.transform = "translateY(-2px)";
            e.currentTarget.style.boxShadow = "0 8px 25px rgba(106, 156, 182, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.3)";
          }
        }}
        onMouseLeave={(e) => {
          if (!isLoading) {
            e.currentTarget.style.transform = "translateY(0)";
            e.currentTarget.style.boxShadow = "0 4px 15px rgba(106, 156, 182, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2)";
          }
        }}
      >
        {isLoading ? "生成中..." : "法話を生成"}
      </button>
    </form>
  );
}
