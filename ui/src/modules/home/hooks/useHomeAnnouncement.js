import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  selectAnnouncement,
  selectIsLoading,
  selectAnnouncementSource,
  selectError,
  fetchAnnouncement,
} from '../state/homeSlice';

export const useHomeAnnouncement = () => {
  const dispatch = useDispatch();
  const announcement = useSelector(selectAnnouncement);
  const isLoading = useSelector(selectIsLoading);
  const source = useSelector(selectAnnouncementSource);
  const error = useSelector(selectError);

  useEffect(() => {
    dispatch(fetchAnnouncement());
  }, [dispatch]);

  return {
    announcement,
    isLoading,
    source,
    error,
  };
};
