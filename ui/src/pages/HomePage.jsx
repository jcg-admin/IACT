import { lazy, Suspense } from 'react';

const HomeModule = lazy(() => import('@modules/home/HomeModule'));

function HomePage() {
  return (
    <div className="page-container">
      <Suspense fallback={<div>Cargando modulo...</div>}>
        <HomeModule />
      </Suspense>
    </div>
  );
}

export default HomePage;
