using System.ComponentModel;
using System.Threading.Tasks;
using System.Windows;
using Nova.Wpf.Dependency;
using PD2StatusWin.Config;

namespace PD2StatusWin.Main;

public class PD2SModel : DependencyObject
{
    #region property config
    public static readonly DependencyProperty configProperty = DependencyProperty.Register(
        "config",
        typeof(PD2SConfig),
        typeof(PD2SModel),
        new FrameworkPropertyMetadata(default(PD2SConfig), FrameworkPropertyMetadataOptions.BindsTwoWayByDefault)
    );

    public PD2SConfig config { get => (PD2SConfig) _mtAccessor.GetValue(configProperty); set => _mtAccessor.SetValue(configProperty, value); }
    #endregion

    #region property loaded
    public static readonly DependencyProperty loadedProperty = DependencyProperty.Register(
        "loaded",
        typeof(bool),
        typeof(PD2SModel),
        new FrameworkPropertyMetadata(default(bool), FrameworkPropertyMetadataOptions.BindsTwoWayByDefault)
    );

    public bool loaded { get => (bool) _mtAccessor.GetValue(loadedProperty); set => _mtAccessor.SetValue(loadedProperty, value); }
    #endregion
    
    public static PD2SModel instance { get; } = new();
    private readonly DependencyPropertyMultiThreadAccessor<PD2SModel> _mtAccessor;

    public PD2SModel()
    {
        _mtAccessor = new DependencyPropertyMultiThreadAccessor<PD2SModel>(this);
        _initModel();
    }

    private void _initModel()
    {
        if (DesignerProperties.GetIsInDesignMode(this)) return;

        config = new PD2SConfig();
        config.loadConfig();
    }
    
    public async Task destroy()
    {
        // ReSharper disable once ConditionIsAlwaysTrueOrFalse
        if (config != null) await config.destroy();
    }

    public void onLoaded()
    {
        loaded = true;
    }
}
