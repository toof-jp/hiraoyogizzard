interface LoadingSpinnerProps {
  message?: string;
}

export function LoadingSpinner({ message = "読み込み中..." }: LoadingSpinnerProps) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '40px 20px',
      textAlign: 'center'
    }}>
      <div style={{
        position: 'relative',
        width: '120px',
        height: '120px',
        marginBottom: '24px'
      }}>
        {/* 複数の波紋を作成 */}
        <div className="ripple" style={{ animationDelay: '0s' }}></div>
        <div className="ripple" style={{ animationDelay: '0.5s' }}></div>
        <div className="ripple" style={{ animationDelay: '1s' }}></div>
        <div className="ripple" style={{ animationDelay: '1.5s' }}></div>
      </div>
      <p style={{
        margin: 0,
        color: '#5a6b7d',
        fontSize: '16px',
        fontWeight: '500',
        letterSpacing: '0.5px'
      }}>{message}</p>
      <style>{`
        .ripple {
          position: absolute;
          top: 50%;
          left: 50%;
          width: 0;
          height: 0;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(106, 156, 182, 0.3) 0%, rgba(106, 156, 182, 0.1) 50%, transparent 70%);
          border: 2px solid rgba(106, 156, 182, 0.4);
          transform: translate(-50%, -50%);
          animation: rippleAnimation 2s ease-out infinite;
        }

        @keyframes rippleAnimation {
          0% {
            width: 0;
            height: 0;
            opacity: 1;
            border-width: 2px;
          }
          50% {
            width: 60px;
            height: 60px;
            opacity: 0.7;
            border-width: 1px;
          }
          100% {
            width: 120px;
            height: 120px;
            opacity: 0;
            border-width: 0;
          }
        }
      `}</style>
    </div>
  );
}