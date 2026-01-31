import { useState } from 'react';
import { Shield, Bell, Moon } from 'lucide-react';
// import { connectToMongoDB } from '../lib/mongodb'; // Removed: not for frontend use

export default function Settings() {
  const [settings, setSettings] = useState({
    theme: 'dark',
    notifications: true,
    autoComplete: true,
    saveHistory: true
  });



  return (
    <div className="py-24 px-4">
      <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-[#00ff00] to-[#00cc00]">
        Settings
      </h1>
      <p className="text-gray-400 mb-8 text-lg">Configure your database assistant</p>

      <div className="space-y-6">

        <div className="border border-[#00ff00]/30 rounded-lg p-6 bg-black/30">
          <div className="flex items-center mb-4">
            <Shield className="h-5 w-5 text-[#00ff00] mr-2" />
            <h2 className="text-xl font-semibold text-[#00ff00]">Security Settings</h2>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-white">Save Query History</label>
              <input
                type="checkbox"
                checked={settings.saveHistory}
                onChange={(e) => setSettings({...settings, saveHistory: e.target.checked})}
                className="w-5 h-5 rounded border-[#00ff00]/30 text-[#00ff00] focus:ring-[#00ff00]/50 bg-black/50"
              />
            </div>
          </div>
        </div>

        <div className="border border-[#00ff00]/30 rounded-lg p-6 bg-black/30">
          <div className="flex items-center mb-4">
            <Bell className="h-5 w-5 text-[#00ff00] mr-2" />
            <h2 className="text-xl font-semibold text-[#00ff00]">Notifications</h2>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-white">Enable Notifications</label>
              <input
                type="checkbox"
                checked={settings.notifications}
                onChange={(e) => setSettings({...settings, notifications: e.target.checked})}
                className="w-5 h-5 rounded border-[#00ff00]/30 text-[#00ff00] focus:ring-[#00ff00]/50 bg-black/50"
              />
            </div>
          </div>
        </div>

        <div className="border border-[#00ff00]/30 rounded-lg p-6 bg-black/30">
          <div className="flex items-center mb-4">
            <Moon className="h-5 w-5 text-[#00ff00] mr-2" />
            <h2 className="text-xl font-semibold text-[#00ff00]">Appearance</h2>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-white">Auto-Complete</label>
              <input
                type="checkbox"
                checked={settings.autoComplete}
                onChange={(e) => setSettings({...settings, autoComplete: e.target.checked})}
                className="w-5 h-5 rounded border-[#00ff00]/30 text-[#00ff00] focus:ring-[#00ff00]/50 bg-black/50"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}