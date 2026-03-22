// Robot Image Component with lazy loading and optimization
interface RobotImageProps {
  src: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  loading?: 'lazy' | 'eager';
}

export function RobotImage({ 
  src, 
  alt, 
  className = '', 
  width, 
  height, 
  loading = 'lazy' 
}: RobotImageProps) {
  return (
    <img
      src={src}
      alt={alt}
      className={className}
      width={width}
      height={height}
      loading={loading}
      style={{
        maxWidth: '100%',
        height: 'auto',
        objectFit: 'cover',
        borderRadius: '12px'
      }}
    />
  );
}
