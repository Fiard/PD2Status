using System.Windows;
using Nova.Wpf.Purgatory.Dependency;

namespace PD2StatusWin.Config;

public class PD2SConfig : DependencyConfig<PD2SConfig>
{
    #region property token
    public static readonly DependencyProperty tokenProperty = DependencyProperty.Register(
        "token",
        typeof(string),
        typeof(PD2SConfig),
        new FrameworkPropertyMetadata(default(string), FrameworkPropertyMetadataOptions.BindsTwoWayByDefault)
    );

    public string token { get => (string) _mtAccessor.GetValue(tokenProperty); set => _mtAccessor.SetValue(tokenProperty, value); }
    #endregion
    
    public PD2SConfig() : base("PD2Status/MainConfig.json")
    {
        
    }
}
