const path = require('path');

module.exports = {
  packagerConfig: {
    icon: path.join(__dirname,'src/icons/maw'),
  },
  rebuildConfig: {},
  makers: [
    {
      name: '@electron-forge/maker-squirrel',
      config: {
        // An URL to an ICO file to use as the application icon (displayed in Control Panel > Programs and Features).
        iconUrl: 'http://127.0.0.1:8000/media/maw.ico',
        // The ICO file to use as the icon for the generated Setup.exe
        setupIcon: path.join(__dirname,'src/icons/maw.ico'),
      },
    },
    {
      name: '@electron-forge/maker-zip',
      config: {
        icon: path.join(__dirname,'src/icons/maw.icns')
      },
      platforms: ['darwin'],
    },
    {
      name: '@electron-forge/maker-deb',
      config: {},
    },
    {
      name: '@electron-forge/maker-rpm',
      config: {},
    },
  ],
};
