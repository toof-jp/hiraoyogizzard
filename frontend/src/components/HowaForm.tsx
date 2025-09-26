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
    <form onSubmit={handleSubmit} style={{ marginBottom: "32px" }}>
      <div style={{ marginBottom: "24px" }}>
        <label
          htmlFor="theme"
          style={{
            display: "block",
            marginBottom: "12px",
            fontWeight: "600",
            fontSize: "16px",
            color: "#2d3748",
            fontFamily: '"Noto Sans JP", sans-serif',
          }}
        >
          法話のテーマ:
        </label>
        <input
          id="theme"
          type="text"
          value={theme}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            setTheme(e.currentTarget.value)
          }
          placeholder="例: 感謝の心"
          required
          style={{
            width: "100%",
            padding: "16px 20px",
            fontSize: "16px",
            border: "2px solid #e2e8f0",
            borderRadius: "12px",
            backgroundColor: "#fafafa",
            transition: "all 0.3s ease",
            outline: "none",
            fontFamily: '"Noto Sans JP", sans-serif',
          }}
          onFocus={(e: React.FocusEvent<HTMLInputElement>) => {
            e.currentTarget.style.border = "2px solid #6a9cb6";
            e.currentTarget.style.backgroundColor = "#ffffff";
            e.currentTarget.style.boxShadow =
              "0 0 0 4px rgba(106, 156, 182, 0.1), 0 4px 15px rgba(106, 156, 182, 0.15)";
            e.currentTarget.style.transform = "translateY(-2px)";
          }}
          onBlur={(e: React.FocusEvent<HTMLInputElement>) => {
            e.currentTarget.style.border = "2px solid #e2e8f0";
            e.currentTarget.style.backgroundColor = "#fafafa";
            e.currentTarget.style.boxShadow = "none";
            e.currentTarget.style.transform = "translateY(0)";
          }}
          onMouseEnter={(e: React.MouseEvent<HTMLInputElement>) => {
            if (document.activeElement !== e.currentTarget) {
              e.currentTarget.style.border = "2px solid #cbd5e0";
              e.currentTarget.style.backgroundColor = "#ffffff";
            }
          }}
          onMouseLeave={(e: React.MouseEvent<HTMLInputElement>) => {
            if (document.activeElement !== e.currentTarget) {
              e.currentTarget.style.border = "2px solid #e2e8f0";
              e.currentTarget.style.backgroundColor = "#fafafa";
            }
          }}
        />
      </div>

      <div style={{ marginBottom: "24px" }}>
        <label
          style={{
            display: "block",
            marginBottom: "12px",
            fontWeight: "600",
            fontSize: "16px",
            color: "#2d3748",
            fontFamily: '"Noto Sans JP", sans-serif',
          }}
        >
          対象者 (複数選択可):
        </label>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
            gap: "12px",
            marginTop: "8px",
          }}
        >
          {audienceOptions.map((option) => (
            <label
              key={option.value}
              style={{
                display: "flex",
                alignItems: "center",
                padding: "12px 16px",
                border: selectedAudiences.includes(option.value)
                  ? "2px solid #6a9cb6"
                  : "2px solid #e2e8f0",
                borderRadius: "12px",
                backgroundColor: selectedAudiences.includes(option.value)
                  ? "rgba(106, 156, 182, 0.1)"
                  : "#fafafa",
                cursor: "pointer",
                transition: "all 0.3s ease",
                position: "relative",
                fontWeight: selectedAudiences.includes(option.value)
                  ? "600"
                  : "500",
                color: selectedAudiences.includes(option.value)
                  ? "#2d3748"
                  : "#4a5568",
                minHeight: "48px",
              }}
              onMouseEnter={(e) => {
                if (!selectedAudiences.includes(option.value)) {
                  e.currentTarget.style.border = "2px solid #cbd5e0";
                  e.currentTarget.style.backgroundColor = "#ffffff";
                  e.currentTarget.style.transform = "translateY(-1px)";
                  e.currentTarget.style.boxShadow =
                    "0 2px 8px rgba(106, 156, 182, 0.1)";
                }
              }}
              onMouseLeave={(e) => {
                if (!selectedAudiences.includes(option.value)) {
                  e.currentTarget.style.border = "2px solid #e2e8f0";
                  e.currentTarget.style.backgroundColor = "#fafafa";
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "none";
                }
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  const checkbox = e.currentTarget.querySelector(
                    'input[type="checkbox"]'
                  ) as HTMLInputElement;
                  checkbox?.click();
                }
              }}
              tabIndex={0}
            >
              <input
                type="checkbox"
                checked={selectedAudiences.includes(option.value)}
                onChange={(e) =>
                  handleAudienceChange(option.value, e.target.checked)
                }
                style={{
                  position: "absolute",
                  opacity: 0,
                  width: 0,
                  height: 0,
                }}
              />
              <div
                style={{
                  width: "20px",
                  height: "20px",
                  borderRadius: "4px",
                  border: selectedAudiences.includes(option.value)
                    ? "2px solid #6a9cb6"
                    : "2px solid #cbd5e0",
                  backgroundColor: selectedAudiences.includes(option.value)
                    ? "#6a9cb6"
                    : "transparent",
                  marginRight: "8px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  transition: "all 0.2s ease",
                  flexShrink: 0,
                }}
              >
                {selectedAudiences.includes(option.value) && (
                  <span
                    style={{
                      color: "white",
                      fontSize: "12px",
                      fontWeight: "bold",
                      lineHeight: 1,
                    }}
                  >
                    ✓
                  </span>
                )}
              </div>
              <span style={{ fontSize: "14px" }}>{option.label}</span>
            </label>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        style={{
          padding: "16px 32px",
          fontSize: "16px",
          fontWeight: "500",
          fontFamily: '"Noto Serif JP", serif',
          background: isLoading
            ? "linear-gradient(135deg, #cbd5e0 0%, #a0aec0 100%)"
            : "linear-gradient(135deg, #6a9cb6 0%, #5a8ca0 100%)",
          color: "white",
          border: "1px solid rgba(255, 255, 255, 0.2)",
          borderRadius: "8px",
          cursor: isLoading ? "not-allowed" : "pointer",
          transition: "all 0.3s ease",
          boxShadow: isLoading
            ? "none"
            : "0 4px 15px rgba(106, 156, 182, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2)",
          letterSpacing: "0.02em",
          position: "relative",
          overflow: "hidden",
        }}
        onMouseEnter={(e) => {
          if (!isLoading) {
            e.currentTarget.style.transform = "translateY(-2px)";
            e.currentTarget.style.boxShadow =
              "0 8px 25px rgba(106, 156, 182, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.3)";
          }
        }}
        onMouseLeave={(e) => {
          if (!isLoading) {
            e.currentTarget.style.transform = "translateY(0)";
            e.currentTarget.style.boxShadow =
              "0 4px 15px rgba(106, 156, 182, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2)";
          }
        }}
      >
        {isLoading ? "生成中..." : "法話を生成"}
      </button>
    </form>
  );
}
