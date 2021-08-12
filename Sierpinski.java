import java.awt.*;
import edu.princeton.cs.algs4.StdDraw;

public class Sierpinski {
	public static void main(String[] args) {
		// Skölun n’ stuff
		StdDraw.setCanvasSize(1024,1024);
		double sc = 0.05;
		int N = Integer.parseInt(args[0]);
		
		double[] x = {0.18-sc, 0.5, 1-0.18+sc};
		double[] y = {0.7928+2.46*sc, 0.1, 0.7928+2.46*sc};
		
		SieTri(N,x,y);

        double h1 = 0.125;
        double h2 = 0.114;
        // StdDraw.line(0.2, 0.58+0.09+h1, 0.8, 0.58+0.09+h1);
        // StdDraw.line(0.2, 0.58+0.09-h2, 0.8, 0.58+0.09-h2);
		
		Font font = new Font("SansSerif",Font.PLAIN,2*132+16);
        // Font font2 = new Font("Helvetica", Font.PLAIN, 2*132+16);
		StdDraw.setFont(font);
		StdDraw.setPenRadius(0.2);
		StdDraw.text(0.5,0.58+0.09,"\u222E", 20*(1+sc));
        // StdDraw.setPenColor(StdDraw.RED);
        // StdDraw.setFont(font2);
        // StdDraw.text(0.5,0.58+0.09,"\u222E",20*(1+sc));
        // StdDraw.setPenColor(StdDraw.BLACK);
		
		StdDraw.setPenRadius(0.004);
		StdDraw.polygon(x,y);
		
		StdDraw.save("Stigull.png");
        // System.out.println(font.getFontName());
        // System.out.println(font2.getFontName());
		
	}
	
	public static void drawTri(double[] x, double[] y) {
		StdDraw.setPenColor(StdDraw.BLACK);
		StdDraw.setPenRadius(0.004);
    //StdDraw.filledPolygon(x,y);
		StdDraw.polygon(x,y);
	}
	
	public static void SieTri(int n, double[] x, double[] y) {
		if (n == 0) {
			drawTri(x,y);
			return;
		}

		double[] x1 = new double[3]; // x-hnit left
		x1[0] = x[0];
		x1[1] = (x[1]+x[0])/2;
		x1[2] = x[1];
		
		double[] x2 = new double[3]; // x-hnit top
		x2[0] = (x[1]+x[0])/2;
		x2[1] = x[1];
		x2[2] = (x[2]+x[1])/2;
		
		double[] x3 = new double[3]; // x-hnit right
		x3[0] = x[1];
		x3[1] = (x[1]+x[2])/2;
		x3[2] = x[2];
		
		double[] y1_3 = new double[3]; // y-hnit left&right
		y1_3[0] = y[0];
		y1_3[1] = (y[1]+y[0])/2;
		y1_3[2] = y[2];
		
		double[] y2 = new double[3]; // y-hnit top
		y2[0] = y1_3[1];
		y2[1] = y[1];
		y2[2] = y1_3[1];
		
		SieTri(n-1, x1, y1_3); 	// low left
		SieTri(n-1, x2, y2); 	// top
		SieTri(n-1, x3, y1_3);	// low right
		
	}
}