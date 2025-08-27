tailwind.config = {
        theme: {
          extend: {
            colors: {
              solar: {
                50: '#fffbeb',
                100: '#fef3c7',
                200: '#fde68a',
                300: '#fcd34d',
                400: '#fbbf24',
                500: '#f59e0b',
                600: '#d97706',
                700: '#b45309',
                800: '#92400e',
                900: '#78350f',
              },
              night: {
                50: '#f8fafc',
                100: '#f1f5f9',
                200: '#e2e8f0',
                300: '#cbd5e1',
                400: '#94a3b8',
                500: '#64748b',
                600: '#475569',
                700: '#334155',
                800: '#1e293b',
                900: '#0f172a',
              }
            },
            animation: {
              'glow': 'glow 2s ease-in-out infinite alternate',
              'float': 'float 3s ease-in-out infinite',
              'slide-in': 'slideIn 0.5s ease-out',
            },
            keyframes: {
              glow: {
                '0%': { boxShadow: '0 0 20px rgba(251, 191, 36, 0.5)' },
                '100%': { boxShadow: '0 0 30px rgba(251, 191, 36, 0.8)' }
              },
              float: {
                '0%, 100%': { transform: 'translateY(0px)' },
                '50%': { transform: 'translateY(-10px)' }
              },
              slideIn: {
                '0%': { opacity: '0', transform: 'translateY(20px)' },
                '100%': { opacity: '1', transform: 'translateY(0)' }
              }
            }
          }
        }
      }