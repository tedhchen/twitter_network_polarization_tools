# Preparation
setwd('')

# Colours
orng.c<-"#fcae91FF"
purp.c<-"#7828a0FF"
gren.c<-"#46aa96FF"
lgry.c<-"#dcdcdcFF"
mgry.c<-"#8c8c8cFF"
dgry.c<-"#333333FF"

# Loading Data
rwc <- read.csv('textoverlaps_parties_climate_30-1_lax_sbm_search2.csv', as.is = T, encoding = 'UTF-8')
rwc <- read.csv('hastext_climate_30-1_sbm_search.csv', as.is = T, encoding = 'UTF-8')
rwc <- read.csv('hasht_topics_85-1_sbm_search.csv', as.is = T, encoding = 'UTF-8')

# Generating Measures
rwc <- data.frame(rwc, t(apply(rwc[,8:1007], 1, function(x){quantile(x, c(0.975, 0.5, 0.025))})))
colnames(rwc)[1008:1010] <- c('upper', 'median', 'lower')
# rwc$density <- apply(rwc[,which(colnames(rwc) %in% c('n_nodes', 'n_edges'))], 1, function(x){x[2]/((x[1]*(x[1]-1))/2)})

# Plotting
pdf('polarizationplot_textoverlaps_parties_climate_30-1_lax_sbm_search2.pdf', height = 5, width = 10)
par(mar = c(5, 5, 1, 1) + 0.1)
n_roll <- 5
for(i in 1:length(unique(rwc$name))){
  upper <- zoo::rollmean(rwc[which(rwc$name == unique(rwc$name)[i]), 'upper'], n_roll)
  lower <- zoo::rollmean(rwc[which(rwc$name == unique(rwc$name)[i]), 'lower'], n_roll)
  duration <- length(upper)
  plot.new()
  plot.window(xlim = c(1, duration), ylim = c(-1.2, 1), xaxs = 'i')
  abline(h = 0)
  
  
  polygon(x = c(1:duration, duration:1), y = c(upper, rev(lower)), col = adjustcolor(orng.c, alpha.f = 0.8), border = NA)
  lines(x = 1:duration, y = zoo::rollmean(rwc[which(rwc$name == unique(rwc$name)[i]), 'median'], n_roll), 
        col = grey(0.2), lwd = 2, lend = 1)
  
  axis(1, at = c(seq(1, duration, 7), duration), labels = F)
  text(c(seq(1, duration, 7), duration), par("usr")[3]-0.12, 
       labels = c(as.character(seq((as.Date('2019-02-18') + n_roll - 1), as.Date('2019-04-14'), 7)), 'Election'), 
       srt = 20, adj = 1, xpd = TRUE, cex = 0.8)
  axis(2)
  abline(v = duration, lwd = 1, lend = 1, lty = 1, col = 'black')
  topics <- strsplit(unique(rwc$name)[i], '_')[[1]]
  if(length(topics) == 3){
    topic <- paste(topics[1], topics[2], sep = ' and ')
  } else {topic <- topics[1]}
  legend('bottomleft', legend = paste('Network based on ', topic, '.', sep = ''), x.intersp = 0, bty = 'n', cex = 0.9)
  box()
  title(ylab = 'Polarization Score'); title(xlab = 'Last Day of 30-Day Period', line = 3.5)
}
dev.off()

rwc_density <- density(rwc$median)
rwc_density$y[c(1, length(rwc_density$y))] <- 0
pdf('polarizationdistribution_hasht_topics_85-1_sbm_search.pdf', height = 10, width = 10)
plot.new()
plot.window(ylim = c(0, max(rwc_density$y)), xlim = c(-0.5, 1.1))
polygon(density(rwc$median), col = adjustcolor(orng.c, alpha.f = 0.8), border = orng.c)
axis(1);axis(2)
title(xlab = 'Polarization Score', ylab = 'Density')
box()
sapply(strsplit(rwc$name[order(rwc$median, decreasing = T)][1:10], '_'), '[', 1)
dev.off()

