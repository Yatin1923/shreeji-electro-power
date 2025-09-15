export const fadeInUp = {
    hidden: { opacity: 0, y: 20 },
    show: (delay: number = 0) => ({
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, delay },
    }),
  };
  