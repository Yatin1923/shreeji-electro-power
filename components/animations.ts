export const fadeInUp = {
    hidden: { opacity: 0, y: 20 },
    show: (delay: number = 0) => ({
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, delay },
    }),
  };

  export const slideInLeft = {
    hidden: { opacity: 0, x: -50 },
    show: (i: number = 1) => ({
      opacity: 1,
      x: 0,
      transition: {
        duration: 0.6,
        delay: i * 0.2, 
      },
    }),
  }
  
  