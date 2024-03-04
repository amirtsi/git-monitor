import React, { useState, useEffect } from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import CircularProgress from '@mui/material/CircularProgress';
import { Typography, Box, Button } from '@mui/material';

const PullRequestList = () => {
  const [pullRequests, setPullRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sortByDateAsc, setSortByDateAsc] = useState(true);

  useEffect(() => {
    const fetchPullRequests = async () => {
      setLoading(true);
      try {
        const response = await fetch('http://ec2-13-60-5-251.eu-north-1.compute.amazonaws.com:8000/api/v1/monitor_router/pull-requests');
        if (!response.ok) {
          throw new Error('Failed to fetch pull requests');
        }
        const data = await response.json();
        setPullRequests(data);
      } catch (error) {
        console.error('Error fetching pull requests:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPullRequests();
  }, []);

  const handleSortByDate = () => {
    const sortedPullRequests = [...pullRequests];
    sortedPullRequests.sort((a, b) => {
      if (sortByDateAsc) {
        return new Date(a.date) - new Date(b.date);
      } else {
        return new Date(b.date) - new Date(a.date);
      }
    });
    setPullRequests(sortedPullRequests);
    setSortByDateAsc(!sortByDateAsc);
  };

  const handleImageDownload = async (screenshotPath) => {
    const baseUrl = 'http://ec2-13-60-5-251.eu-north-1.compute.amazonaws.com:8000/api/v1/monitor_router/';
    const imageUrl = `${baseUrl}${screenshotPath}`;

    try {
      const response = await fetch(imageUrl);
      if (!response.ok) {
        throw new Error('Failed to download image');
      }

      const arrayBuffer = await response.arrayBuffer();
      const blob = new Blob([arrayBuffer], { type: response.headers.get('Content-Type') });
      const blobUrl = URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = screenshotPath.split('/').pop();

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      setTimeout(() => URL.revokeObjectURL(blobUrl), 100);
    } catch (error) {
      console.error('Error downloading image:', error);
    }
  };

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        GitHub Pull Requests Monitoring
      </Typography>
      <Box display="flex" justifyContent="space-between" alignItems="center" marginBottom={2}>
        <Typography variant="body1" gutterBottom>
          Sort by Date:
        </Typography>
        <Button variant="contained" onClick={handleSortByDate}>
          {sortByDateAsc ? 'Ascending' : 'Descending'}
        </Button>
      </Box>
      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }} aria-label="simple table">
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>User</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Download Image</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {pullRequests.map((pr) => (
                <TableRow key={pr.id} hover>
                  <TableCell>{pr.id}</TableCell>
                  <TableCell>{pr.title}</TableCell>
                  <TableCell>{pr.user ? pr.user.login : 'No user information'}</TableCell>
                  <TableCell>{pr.date}</TableCell>
                  <TableCell>
                    {pr.screenshot_path && (
                      <button
                        style={{ textDecoration: 'underline', cursor: 'pointer', background: 'none', border: 'none', color: 'blue' }}
                        onClick={() => handleImageDownload(pr.screenshot_path)}
                      >
                        Download
                      </button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </div>
  );
};

export default PullRequestList;
