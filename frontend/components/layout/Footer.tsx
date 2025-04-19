export default function Footer() {
    return (
      <footer className="bg-green-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col items-center justify-center">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-green-400 to-green-500 flex items-center justify-center mr-2">
                <div className="text-white font-bold text-sm">S</div>
              </div>
              <span className="text-xl font-bold text-white">Sambot</span>
            </div>
            <p className="text-green-200 text-center text-sm">
              Personal AI trading assistant for monitoring market signals.
            </p>
            <p className="mt-4 text-green-300 text-xs">
              &copy; {new Date().getFullYear()} Sambot. For personal use only. Trading involves risk.
            </p>
          </div>
        </div>
      </footer>
    );
  }