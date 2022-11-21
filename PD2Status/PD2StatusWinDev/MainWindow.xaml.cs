using System;
using System.ComponentModel;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using Nova.Core.Log;
using Nova.Kernel.Shared.Log;
using Nova.Wpf.Runtime;
using PD2StatusWin.Main;

namespace PD2StatusWin
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow
    {
        private static readonly LogLib _log = new LogLib(nameof(MainWindow));
        
        public MainWindow()
        {
            InitializeComponent();
        }
        
        private bool _trueClosing;
        private bool _alreadyClosing;
        private async void closing(object sender, CancelEventArgs e)
        {
            if (_trueClosing) return;
            e.Cancel = true;
            
            if (_alreadyClosing) return;
            _alreadyClosing = true;

            Visibility = Visibility.Collapsed;
            
            try {
                await Task.Run(async () => await PD2SModel.instance.destroy());
                _finalCleanup();
            } catch (Exception ex) {
                Log.error("MainWindow", $"closing: failed with {ex}");
                Log.error("MainWindow", "Process will be terminated forcely in 2 seconds ...");
                
                new Thread(() => {
                    Thread.Sleep(2000);
                    Log.error("MainWindow", "ForceExit thread timeout passed, force exiting"); //log's error flushes automatically
                    Application.Current.ExitAnyThread(-101);
                }) { Name = "ForceExit", IsBackground = true }.Start();
            } finally {
                CoreLogManager.flush();
                _trueClosing = true;
                Close();
            }
        }
        
        private void _finalCleanup()
        {
            try {
                Dispatcher?.InvokeShutdown();
            } catch (Exception ex) {
                _log.error($"Dispatcher shutdown failed with exception {ex}");
            }
        }
    }
}
