import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  selectAnnouncement,
  selectIsLoading,
  fetchAnnouncement,
} from '../state/homeSlice';

export const useHomeAnnouncement = () => {
  const dispatch = useDispatch();
  const announcement = useSelector(selectAnnouncement);
  const isLoading = useSelector(selectIsLoading);

  useEffect(() => {
    dispatch(fetchAnnouncement());
  }, [dispatch]);

  return {
    announcement,
    isLoading,
  };
};
