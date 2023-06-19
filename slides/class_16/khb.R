khb <- function(reduced, full, corrected.se=FALSE, med.sandwich=NULL, glm.sandwich=FALSE,  savefs=FALSE){
  ## Variables in reduced model
  keyvar <- attr(reduced$terms, "term.labels")
  ## Variables in full model
  vf <- attr(full$terms, "term.labels")
  ## Define mediators as variable present only in full model
  mediators <- vf[!(vf %in% keyvar)]
  message(" [>] Mediators: ", paste(mediators, collapse=", "))
  datamm <- model.matrix(full)
  if(inherits(full, "clm")){
    datamm <- datamm$X
  }
  datammdf <- as.data.frame(datamm)
  ## Some mediators may have several z variable (ie factors)
  getVarList <- function(kv){
    ## position of variables in term assign list
    ikv <- match(kv, vf)
    kvList <- list()
    for(i in seq_along(kv)){
      kvList[[kv[i]]] <- colnames(datamm)[attr(datamm, "assign") == ikv[i]]
    }
    return(kvList)
  }
  keyvarList <- getVarList(keyvar)
  mediatorList <- getVarList(mediators)
  allkeyvar <- unlist(keyvarList, use.names=F) ##colnames(datamm)[attr(datamm, "assign") %in% ikeyvar]
  allmediators <- unlist(mediatorList, use.names=F) ##colnames(datamm)[attr(datamm, "assign") %in% imediators]
  nz <- length(allmediators)
  ## Choosing covariance estimator
  if(is.null(med.sandwich)){
    med.sandwich <- any(sapply(datammdf[, allmediators], function(x){return(length(unique(x))==2)}))
  }
  stata.sandwich <- function(...){
    return(sandwich(..., adjust=TRUE))
  }
  vcovfunc <- if(med.sandwich){stata.sandwich} else{ vcov}
  vcovglm <- if(glm.sandwich){stata.sandwich} else{vcov}
  
  ## Return object
  ret <- list()
  ## Storing summary informations.
  ff <- list()
  for(z in allmediators){
    ff[[z]] <- as.formula(paste0("`",z,"`~`",paste(c(allkeyvar), collapse="`+`"),"`"))
  }
  ##getAdjustedModel <- function(reduced){
  ## Try to get the same as stata
  fitsur <- systemfit(ff, data=datammdf, method="SUR", control=systemfit.control(maxiter = 2, methodResidCov = "noDfCor"))
  ## Compute residuals 
  zresid <- resid(fitsur)
  names(zresid) <- paste("KHB__KHB__", names(zresid), sep="")
  ## Updating the reduced model to include the 
  adjusted <- update(reduced, formula = as.formula(paste0(".~.+", paste0("`KHB__KHB__", allmediators,"`", collapse=" + "))), data = data.frame(model.frame(reduced), zresid))
  
  ##	return(adjusted)
  ##}
  ##adjusted <- getAdjustedModel(reduced)
  ## Needed for statistical signif
  ## sgrzr <- summary(grzr)
  ## sgf <- summary(gf)
  zcovmat <- matrix(0, ncol=2*nz, nrow=2*nz)
  zcovmat[1:nz, 1:nz] <- vcovglm(full)[allmediators, allmediators]
  if(savefs){
    estimation <- list()
  }
  adjustedCoef  <- coeftest(adjusted, vcov.=vcovglm)
  fullCoef <- coeftest(full, vcov.=vcovglm)
  reducedCoef <- coef(reduced)
  ckgr <- coef(reduced)[allkeyvar]
  ckgrzr <- adjustedCoef[allkeyvar, 1]
  ckgf <- fullCoef[allkeyvar, 1]
  sum_conf <- data.frame(Ratio=ckgrzr/ckgf, Percentage=100*(ckgrzr-ckgf)/ckgrzr, 
                         Rescaling=ckgrzr/ckgr)
  rownames(sum_conf) <- allkeyvar
  
  for(kk in allkeyvar){
    ret[[kk]] <- list()
    medSUR <- match(paste(allmediators, kk, sep="_"), names(coef(fitsur)))
    zcoef <- coef(fitsur)[medSUR]
    names(zcoef) <- allmediators
    zcovmat[nz+1:nz, nz+1:nz] <- vcovfunc(fitsur)[medSUR, medSUR]
    a <- c(zcoef, fullCoef[allmediators, 1])
    sdconf <-  sqrt(t(a) %*% zcovmat %*% a)
    if(savefs){
      estimation[[kk]] <- list(a=a, sigma=zcovmat, se=sdconf) 
    }
    
    res <- matrix(0, ncol=4, nrow=3)
    colnames(res) <- c("Estimate", "Std. Error", "z value", "Pr(>|z|)")
    rownames(res) <- c("Reduced", "Full", "Diff")
    
    res[1, ] <- adjustedCoef[kk, ]
    if(corrected.se){
      SIGMA <- matrix(0, nrow=2*nz+1, ncol=2*nz+1)
      intvar <- c(kk, allmediators)
      aa <- c(zcoef, fullCoef[intvar, 1])
      SIGMA[1:(1+nz), 1:(1+nz)] <- vcovglm(full)[intvar, intvar]
      SIGMA[nz+1+1:nz,nz+1+1:nz] <- zcovmat[nz+1:nz, nz+1:nz]
      res[1, 2] <- sqrt(t(aa) %*% SIGMA %*% aa)
      res[1, 3] <- res[1, 1]/res[1, 2]
      res[1,4] <- 2 * pnorm(-abs(res[1, 3]))
      
    }
    res[2, ] <- fullCoef[kk, ]
    res[3, ] <- res[1,]-res[2, ]
    res[3, 2] <- sdconf
    res[3, 3] <- res[3, 1]/sdconf
    res[3,4] <- 2 * pnorm(-abs(res[3, 3]))
    ret[[kk]]$table <- res
    
    res <- matrix(0, ncol=6, nrow=1+nz)
    colnames(res) <- c("% diff", "% effect", "Estimate", "Std. Error", "z value", "Pr(>|z|)")
    rownames(res) <- c("Grand Indirect", allmediators)
    res["Grand Indirect", ] <- c(100, 100*sum_conf[kk, "Percentage"], ret[[kk]]$table[3, 1:4])
    for(zz in allmediators){
      izz <- match(zz, allmediators)
      res[zz, 3] <- fullCoef[zz, 1]*zcoef[zz]
      izzpos <- c(izz, nz+izz)
      res[zz, 4] <- sqrt(t(a[izzpos]) %*% zcovmat[izzpos,izzpos] %*% a[izzpos])
      res[zz, 5] <- res[zz, 3]/res[zz, 4]
      res[zz, 6] <- 2 * pnorm(-abs(res[zz, 5]))
      res[zz, 1] <- 100*res[zz, 3]/ res[1, 3]
      res[zz, 2] <- 100*res[zz, 3]/ ret[[kk]]$table[1,1]
    }
    ret[[kk]]$detail <- res
    ##ret[[kk]]$ape["Diff"] <- ret$ape["Reduced"] - ret$ape["Full"]
  }
  finalobj <-list(sum_conf=sum_conf, key=ret, reduced=reduced, adjusted=adjusted, full=full,
                  keyvar=keyvarList, mediators=mediatorList)
  if(savefs){
    estimation$fitsur <- fitsur
    finalobj$estimation <- estimation
  }
  class(finalobj) <- "khb"
  return(finalobj)
  
}

#' @rdname khb
#' @param x A khb object
#' @param type Character. The type of information printed (see details).
#' @param keyvar A character vector or \code{NULL} (default). The list of 
#'   variables of interest (for which the change between models are displayed). 
#'   If \code{NULL} (default), all variables of the reduced models are considered as key 
#'   variables.
#' @param disentangle Logical. If \code{FALSE} (default), the contribution of each mediator is not printed.
#' @param ... Arguments passed to other methods.
#' @method print khb
print.khb <- function(x, type="summary", keyvar=NULL, disentangle=FALSE, ...){
  if(type=="models"){
    args <- c(list(Reduced=x$reduced, Adjusted=x$adjusted, Full=x$full), list(...))
    print(do.call(regTable, args), quote=FALSE)
    return(invisible())
  }
  
  cat("KHB method\n")
  cat("Model type:",  class(x$reduced), ifelse(inherits(x$reduced, "glm"),paste0("(", family(x$reduced)$link,")"), "") , "\n")
  varList <- function(vl){
    ret <- character(length(vl))
    names(ret) <- names(vl)
    for(nn in names(vl)){
      vlnn <- vl[[nn]]
      if(length(vlnn)==1 && vlnn==nn){
        ret[nn] <- nn
      }else{
        ret[nn] <- paste0(nn, " (", paste(vlnn, collapse=", "), ")")
      }
    }
    return(paste(ret, collapse=", "))
  }
  cat("Variables of interest: ", varList(x$keyvar), fill=TRUE, sep="")
  cat("Z variables (mediators): ", varList(x$mediators), fill=TRUE, sep="")
  cat("\nSummary of confounding\n")
  printCoefmat(x$sum_conf)
  #cat("\n")
  
  if(is.null(keyvar)){
    keyvar <- names(x$key)
  }else if(length(keyvar)==1 && keyvar==FALSE){
    return(invisible())
  } else{
    cond <- keyvar %in% names(x$key)
    cond2 <- keyvar %in% names(x$keyvar)
    if(any((!cond) & (!cond2))){
      stop(" [!] The following keyvar were not found: ", paste(keyvar[(!cond) & (!cond2)], collapse=", "))
    }
    keyvar <- c(keyvar[cond], unlist(x$keyvar[keyvar[cond2&(!cond)]]))
  }
  for(k in keyvar){
    cat(rep("--", 22),"\n", sep="-")
    cat(k,":\n")
    printCoefmat(x$key[[k]]$table, cs.ind=1:2, tst.ind=3, signif.legend=FALSE)
    if(nrow(x$key[[k]]$detail)>2 && disentangle){
      cat("\n\nDecomposition of the difference:\n")
      printCoefmat(x$key[[k]]$detail[-1,], cs.ind=3:4, tst.ind=5, zap.ind=1:2)
    }
  }
  return(invisible())
}
