using System;
using System.IO;
using System.Threading;
using System.Windows;
using Nova.Core.Log;
using Nova.Kernel.Shared.Log;

namespace PD2StatusWin
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App
    {
        private static readonly LogLib _log = new LogLib(nameof(App));

        public App()
        {
            var appData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            var persistentDataPath = Path.Combine(appData, "Fiard", "PD2Status");
            
            CoreLogManager.initializeCoreLogs(null, Path.GetFullPath(Path.Combine(persistentDataPath, "Logs")));
            _log.report(">>>>>>>> PD2 Status <<<<<<<<");
            LogManager.replaceProcessId("pd2s");
            LogManager.replaceThreadId(Thread.CurrentThread.ManagedThreadId, "--");
        }

        private void OnXamlStartup(object sender, StartupEventArgs e)
        {
            _startup();
        }

        private void _startup()
        {
            Current.ShutdownMode = ShutdownMode.OnMainWindowClose; //re-enable normal shutdown mode
            var mainWindow = new MainWindow();
            Current.MainWindow = mainWindow;

            mainWindow.Show();
        }
    }
}
