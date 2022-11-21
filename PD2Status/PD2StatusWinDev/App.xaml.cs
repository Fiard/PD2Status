using System.Windows;

namespace PD2StatusWin
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App
    {
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
