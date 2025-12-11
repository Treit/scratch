 using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Web;

namespace TestFrameworkApp
{
    internal class Program
    {
        static void Main(string[] args)
        {
            var level = System.Web.AspNetHostingPermissionLevel.Minimal;
            Console.WriteLine(level);

        }
    }
}
