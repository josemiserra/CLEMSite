namespace msite
{
    public class PointEM
    {
        public double x;
        public double y;
        public double z;
        public double r;
        public double t;
        public double m;
        public double bsx;
        public double bsy;

        public PointEM() { x = 0.0; y = 0.0; z = 0.0; r = 0.0; t = 0.0; m = 0.0; bsx = 0; bsy = 0; }
        public PointEM(float px, float py) { x = (double)px; y = (double)py; z = 0.0; r = 0.0; t = 0.0; m = 0.0; bsx = 0; bsy = 0; }
        public PointEM(PointEM p) { x = p.x; y = p.y; z = p.z; r = p.r; t = p.t; m = p.m; bsx = p.bsx; bsy = p.bsy; }
        public PointEM(float px, float py, float pz = 0, float pr = 0, float pt = 0, float pm = 0)
        { x = (double)px; y = (double)py; z = (double)pz; r = (double)pr; t = (double)pt; m = (double)pm; bsx = 0; bsy = 0; }
        public PointEM(double px, double py, double pz, double pr, double pt, double pm)
        { x = px; y = py; z = pz; r = pr; t = pt; m = pm; }
        public PointEM(float px, float py, float pz)
        { x = px; y = py; z = pz; }

        public static PointEM operator +(PointEM c1, PointEM c2)
        {
            return new PointEM(c1.x + c2.x, c1.y + c2.y, c1.z + c2.z, c1.r + c2.r, c1.t + c2.t, c1.m + c2.m);
        }
        public override string ToString()
        {
            return "X :" + x + ",Y :" + y + ",Z :" + z + ",T :" + t + ",M :" + m + ",R :" + r + "\n";
        }
    };
}