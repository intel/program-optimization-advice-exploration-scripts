#include <stdio.h>
#include <math.h>
#include <omp.h>
extern void external();
int X=55;
int glob=99;
int yo(int x, int y, unsigned char id){
	return x*y;
}
int foo(int);
int bar(int*,int);
struct _TGAInfo
{
  unsigned char
    id_length,
    colormap_type,
    image_type;

  unsigned short
    colormap_index,
    colormap_length;

  unsigned char
    colormap_size;

  unsigned short
    x_origin,
    y_origin,
    width,
    height;

  unsigned char
    bits_per_pixel,
    attributes;
};
typedef struct _TGAInfo TGAInfo;
typedef struct _TGAXXXX
{
  unsigned char
    id_length,
    colormap_type,
    image_type;

  unsigned short
    colormap_index,
    colormap_length;

  unsigned char
    colormap_size;

  unsigned short
    x_origin,
    y_origin,
    width,
    height;

  unsigned char
    bits_per_pixel,
    attributes;
}TGAXXXX;

int main(){
	int i,j,k; long long sum1=0,sum2=0;

  TGAInfo tga_info;

  if(sum1 = 0){
	  for(j=0;j<10;j++){
		  sum2 = yo(sum2,j, &tga_info.id_length);
	  }
  }
	bar(&sum1,sum2);
	return 0;
}

int foo(int i){
	return log(i);
}
int bar(int *i, int j){
	return pow(*i,j);
}
