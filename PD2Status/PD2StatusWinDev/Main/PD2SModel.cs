using System.Windows;

namespace PD2StatusWin.Main;

public class PD2SModel : DependencyObject
{
    public static PD2SModel instance { get; } = new();
}
