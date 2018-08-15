#include<cstdio>
const int buf_sz=439999,answer_cnt=3999,str_len=999;
char buf[buf_sz];
int p[answer_cnt][7],f[str_len][str_len];
inline int max(int a,int b){return a>b?a:b;}
inline int lcs(int*_a,int*_b){
	char*a=buf+*_a,*b=buf+*_b;
	int al=_a[1]-*_a,bl=_b[1]-*_b;
	if(!al||!bl)return 0;
	for(int i=0;i<=al;i++)f[i][0]=0;
	for(int i=0;i<=bl;i++)f[0][i]=0;
	for(int i=0;i<al;i++)for(int j=0;j<bl;j++)
		f[i+1][j+1]=a[i]==b[j]?f[i][j]+1:max(f[i][j+1],f[i+1][j]);
	return f[al][bl];
}
int main(){
	//FILE*ans=fopen("answers.txt","r");
	int sz,n=0,score=-1,best,t,v;
	sz=fread(buf,1,sizeof buf,stdin);
	//buf[sz++]='\n';
	//sz+=fread(buf+sz,1,sizeof buf-sz,ans);
	for(int i=0;i<sz;i++)if(buf[i]=='\n')p[++n][0]=i;
	p[++n][0]=sz;
	for(int i=0;i<n;i++){
		for(int j=1;j<7;j++)p[i][j]=p[i+1][0];
		for(int j=p[i][0],c=0;c<6&&j<p[i+1][0];j++)
			if(buf[j]==',')p[i][++c]=j;
	}
	for(int i=1;i<n;i++){
		t=lcs(p[0],p[i]);
		for(int j=0;v=0,j<5;j++,t+=v)for(int k=0;k<5;k++)
			v=max(v,lcs(p[0]+j,p[i]+k));
		if(t>score)score=t,best=i;
	}
	if(score==0)return puts("0"),0;
	v=best,score=-1;
	for(int i=1;i<5;i++){
		t=lcs(p[0]+i,p[v]+5);
		if(t>score)score=t,best=i;
	}
	printf("%d\n",best);
}
